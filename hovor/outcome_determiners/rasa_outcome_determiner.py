from dataclasses import dataclass
from typing import Dict
from hovor.outcome_determiners import SPACY_LABELS
from hovor.outcome_determiners.outcome_determiner_base import OutcomeDeterminerBase
from hovor.planning.outcome_groups.deterministic_outcome_group import (
    DeterministicOutcomeGroup,
)
from hovor import DEBUG
import requests
import json
import random
from nltk.corpus import wordnet
from typing import Union

THRESHOLD = 0.65


@dataclass
class Intent:
    name: str
    entity_assignments: Union[frozenset, None]
    outcome: DeterministicOutcomeGroup
    confidence: float

    def __eq__(self, other):
        return (
            self.name == other.name
            and self.entity_assignments == other.entity_assignments
            and self.outcome == other.outcome
            and self.confidence == other.confidence
        )

    def __lt__(self, other):
        return self.confidence > other.confidence


class RasaOutcomeDeterminer(OutcomeDeterminerBase):
    """Determiner"""

    def __init__(self, full_outcomes, context_variables, intents):
        self.full_outcomes = {outcome["name"]: outcome for outcome in full_outcomes}
        self.context_variables = context_variables
        self.intents = intents

    @staticmethod
    def parse_synset_name(synset):
        return synset.name().split(".")[0]

    def find_rasa_entity(self, entity: str):
        if entity in self.rasa_entities:
            return self.rasa_entities[entity]

    def find_spacy_entity(self, method: str):
        if method in self.spacy_entities:
            if self.spacy_entities[method]:
                return self.spacy_entities[method].pop()

    def initialize_extracted_entities(self, entities: Dict):
        self.spacy_entities = {}
        self.rasa_entities = {}
        for extracted in entities:
            if extracted["entity"] in SPACY_LABELS:
                if extracted["entity"] in self.spacy_entities:
                    self.spacy_entities[extracted["entity"]].append(extracted)
                else:
                    self.spacy_entities[extracted["entity"]] = [extracted]
            else:
                self.rasa_entities[extracted["entity"]] = extracted

    def extract_entity(self, entity: str):
        # spacy
        if type(self.context_variables[entity]["config"]) == dict:
            if self.context_variables[entity]["config"]["extraction"] == "spacy":
                extracted = self.find_spacy_entity(
                    self.context_variables[entity]["config"]["method"].upper()
                )
                if not extracted:
                    # if we can't parse with spacy, try with Rasa (may also return None)
                    extracted = self.find_rasa_entity(entity)
                    if not extracted:
                        return
                    certainty = "maybe-found"
                else:
                    certainty = "found"
        # rasa
        else:
            extracted = self.find_rasa_entity(entity)
            if not extracted:
                if self.spacy_entities.values():
                    extracted = []
                    extracted.extend(
                        val
                        for method_vals in self.spacy_entities.values()
                        for val in method_vals
                    )
                    extracted = random.choice(extracted)
                    certainty = "maybe-found"
                else:
                    return
            else:
                certainty = "found"
        return {
            "extracted": extracted,
            "value": extracted["value"],
            "certainty": certainty,
        }

    def extract_entities(self, intent):
        entities = {}
        # get entities from frozenset
        for entity in {f[0] for f in intent.entity_assignments}:
            # raw extract single entity, then validate
            extracted_info = self.extract_entity(entity)
            if extracted_info:
                extracted_info = self._make_entity_type_sample(
                    entity,
                    self.context_variables[entity]["type"],
                    self.context_variables[entity]["config"],
                    extracted_info,
                )
            else:
                extracted_info = {"certainty": "didnt-find", "sample": None}
            entities[entity] = extracted_info
        return entities

    def extract_intents(self, intents):
        entities = {}
        chosen_intent = None
        entity_assignment_to_out = {
            intent.entity_assignments: intent.outcome
            for intent in intents
            if intent.entity_assignments
        }
        for intent in intents:
            # if this intent expects entities, make sure we extract them
            if intent.entity_assignments != None:
                entities = self.extract_entities(intent)
                # if no entities were successfully extracted
                if {entities[e]["sample"] for e in entities} != {None}:
                    # construct the intent we found
                    # re-assign the entity assignments to what we were actually able to extract
                    # re-assign the outcome to what matches our entity assignments
                    extracted_entity_assignments = frozenset(
                        {
                            k: v["certainty"]
                            for k, v in entities.items()
                            if v["sample"]
                        }.items()
                    )
                    chosen_intent = Intent(
                        intent.name,
                        extracted_entity_assignments,
                        entity_assignment_to_out[extracted_entity_assignments],
                        intent.confidence,
                    )
                    # stop looking for a suitable intent as we have found one that maps to a valid outcome :)
                    # note that this check allows you to use full or partial information depending on how you set up your actions
                    if chosen_intent in intents:
                        break
                    else:
                        # need to reassign to None in case we break on the last intent
                        chosen_intent = None
            else:
                if intent.confidence > THRESHOLD:
                    # stop looking for a suitable intent if the intent extracted doesn't require entities
                    chosen_intent = intent
                    break
        # if we have a fallback, assign all other confidences to 0
        if not chosen_intent:
            for intent in intents:
                if intent.name == "fallback":
                    chosen_intent = intent
                    intent.confidence = 1.0
                else:
                    intent.confidence = 0
        else:
            # in the case that there are multiple intents with the same name and confidence
            # because we're going by entity assignment, we only want the intent that reflects
            # our extracted entity assignment to be chosen. i.e. at this point, an intent share_cuisine where
            # cuisine is "found" and the sister intent share_cuisine where cuisine is "maybe-found" will
            # have the same confidence, but we only want the right one to be chosen.
            for intent in intents:
                if intent.name == chosen_intent.name and intent.entity_assignments != chosen_intent.entity_assignments:
                    intent.confidence = 0
        # rearrange intent ranking
        intents.remove(chosen_intent)
        intents = [chosen_intent] + intents
        ranked_groups = [
            {
                "intent": intent.name,
                "outcome": intent.outcome,
                "confidence": intent.confidence,
            }
            for intent in intents
        ]
        return chosen_intent.name, entities, ranked_groups

    def create_intents(self, r, outcome_groups):
        intent_ranking = {
            ranking["name"]: ranking["confidence"] for ranking in r["intent_ranking"]
        }
        intent_ranking["fallback"] = 0
        intents = []
        for out in outcome_groups:
            out_intent = self.full_outcomes[out.name]["intent"]

            # if dealing with a complex dict intent (i.e. {"cuisine": "maybe-found"}, then check to see
            # if any of the extracted intents require each of the entities mentioned). i.e. for the example
            # mentioned, the intent share_cuisine requires
            if type(out_intent) == dict:
                entity_requirements = frozenset(out_intent.items())
                for intent in intent_ranking:
                    variables = [v[1:] for v in self.intents[intent]["variables"]]
                    detected = False not in {
                        entity_map[0] in variables for entity_map in entity_requirements
                    }
                    if detected:
                        out_intent = intent
                        break
            else:
                variables = [v[1:] for v in self.intents[out_intent]["variables"]]
                entity_requirements = (
                    frozenset({v: "found" for v in variables}.items())
                    if len(variables) > 0
                    else None
                )
                detected = out_intent in intent_ranking
            # we only want to consider intents from each outcome that rasa has detected
            if detected:
                intents.append(
                    Intent(
                        out_intent, entity_requirements, out, intent_ranking[out_intent]
                    )
                )
        intents.sort()
        return intents

    def get_final_rankings(self, input, outcome_groups):
        r = json.loads(
            requests.post(
                "http://localhost:5005/model/parse", json={"text": input}
            ).text
        )

        intents = self.create_intents(r, outcome_groups)
        self.initialize_extracted_entities(r["entities"])

        return self.extract_intents(intents)

    def rank_groups(self, outcome_groups, progress):
        chosen_intent, entities, ranked_groups = self.get_final_rankings(
            progress.json["action_result"]["fields"]["input"], outcome_groups
        )
        ranked_groups = [
            (intent["outcome"], intent["confidence"]) for intent in ranked_groups
        ]
        # shouldn't only add samples for extracted entities; some outcomes don't
        # extract entities themselves but update the values of existing entities
        if chosen_intent:
            for entity, entity_info in entities.items():
                if "sample" in entity_info:
                    progress.add_detected_entity(entity, entity_info["sample"])
            outcome_description = progress.get_description(ranked_groups[0][0].name)
            for update_var, update_config in outcome_description["updates"].items():
                if "value" in update_config and update_var not in entities:
                    if progress.get_entity_type(update_var) == "enum":
                        value = update_config["value"]
                        if update_config["value"] == f"${update_var}":
                            value = progress.actual_context._fields[update_var]
                        progress.add_detected_entity(update_var, value)
        DEBUG("\t top random ranking for group '%s'" % (chosen_intent))
        return ranked_groups, progress

    def _make_entity_type_sample(self, entity, entity_type, entity_config, extracted_info):
        entity_value = extracted_info["value"]
        if entity_type == "enum":
            # lowercase all strings in entity_config, map back to original casing
            entity_config = {e.lower(): e for e in entity_config}
            entity_value = entity_value.lower()
            if entity_value in entity_config:
                extracted_info["sample"] = entity_config[entity_value]
                return extracted_info
            else:
                if "known" in self.context_variables[entity]:
                    if self.context_variables[entity]["known"]["type"] == "fflag":
                        extracted_info["certainty"] = "maybe-found"
                        for syn in wordnet.synsets(entity_value):
                            for option in entity_config:
                                if option in syn._definition.lower():
                                    extracted_info["sample"] = entity_config[option]
                                    return extracted_info
                            for lemma in syn.lemmas():
                                for p in lemma.pertainyms():
                                    p = p.name().lower()
                                    if p in entity_config:
                                        extracted_info["sample"] = entity_config[p]
                                        return extracted_info
                                for d in lemma.derivationally_related_forms():
                                    d = d.name().lower()
                                    if d in entity_config:
                                        extracted_info["sample"] = entity_config[d]
                                        return extracted_info
                            for hyp in syn.hypernyms():
                                hyp = RasaOutcomeDeterminer.parse_synset_name(hyp).lower()
                                if hyp in entity_config:
                                    extracted_info["sample"] = entity_config[hyp]
                                    return extracted_info
                            for hyp in syn.hyponyms():
                                hyp = RasaOutcomeDeterminer.parse_synset_name(hyp).lower()
                                if hyp in entity_config:
                                    extracted_info["sample"] = entity_config[hyp]
                                    return extracted_info
                            for hol in syn.member_holonyms():
                                hol = RasaOutcomeDeterminer.parse_synset_name(hol).lower()
                                if hol in entity_config:
                                    extracted_info["sample"] = entity_config[hol]
                                    return extracted_info
                            for hol in syn.root_hypernyms():
                                hol = RasaOutcomeDeterminer.parse_synset_name(hol).lower()
                                if hol in entity_config:
                                    extracted_info["sample"] = entity_config[hol]
                                    return extracted_info
        elif entity_type == "json":
            extracted_info["sample"] = extracted_info["value"]
            return extracted_info
        else:
            raise NotImplementedError("Cant sample from type: " + entity_type)
        extracted_info["certainty"] = "didnt-find"
        extracted_info["sample"] = None
        return extracted_info
