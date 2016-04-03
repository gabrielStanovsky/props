REASON_LABEL = "reason"
OUTCOME_LABEL = "outcome"
EVENT_LABEL = "event"
CONDITION_LABEL = "condition"
FIRST_ENTITY_LABEL = "sameAs_arg"
SECOND_ENTITY_LABEL = "sameAs_arg"
POSSESSOR_LABEL = "possessor"
POSSESSED_LABEL = "possessed"
ARG_LABEL = "arg"
domain_label = "prop_of"

determiner_dependencies = ["det"]
conjunction_dependencies = ["cc"]
aux_dependencies = ["aux", "auxpass"]
aux_cop_dependencies = aux_dependencies + ["cop"]
passive_dependencies = ["auxpass"]# "csubjpass", "nsubjpass" also indicate passive, but must come with auxpass in the general case. For other cases see json_files/not_auxpass.json
negation_dependencies = ["neg"]
time_dependencies = ["tmod"]
subject_dependencies = ["subj","nsubj","nsubjpass","csubj","csubjpass","xsubj"]
object_dependencies = ["obj","dobj","iobj","pobj"]
clausal_complements = ["acomp","xcomp","comp","ccomp"]#"vmod"]#"dep"]
rare_dependencies = ["dep","parataxis","expl"]
arguments_dependencies = ["arg","agent"] + object_dependencies + subject_dependencies + [domain_label,FIRST_ENTITY_LABEL,SECOND_ENTITY_LABEL,POSSESSED_LABEL,POSSESSOR_LABEL,OUTCOME_LABEL,REASON_LABEL,CONDITION_LABEL,EVENT_LABEL]
clausal_complement = ["xcomp"]
adverb_dependencies = ["advmod", "advcl"]
appositional_dependencies = ["appos"]
prepositions_dependencies = ["prep"]
prt_dependency = "prt"
adjectival_mod_dependencies = ["amod","acomp"]
mod_labels = ["amod", "vmod"] + adverb_dependencies
determined_labels = ["NNP"]
definite_determiners = ["the","this","that","these","those","another"]
relclause_dependencies = ["rcmod"]
relclause_markers = ["that","which","who","whom"]
mark_labels = ["mark","advmod"]
clausal_modifiers_labels = ["advcl","dep"]
labels_ban = ["preconj"]
filter_labels_ban = lambda n:n.parent_relation not in labels_ban
#single labels = not lists
POSS_LABEL = "poss"
MARK_LABEL = "mark"
EXPL_LABEL = 'expl'
SOURCE_LABEL = 'source'
MODIFIER_LABEL = "modifier"
POSSESSIVE_LABEL = "possessive"
SUBJ_LABEL  = "subj"
OBJECT_LABEL = "obj"
DIRECT_OBJECT_LABEL = "dobj"
INDIRECT_OBJECT_LABEL = "iobj"

definite_label = "definite"
indefinite_label = "indefinite"



# POS tags
VB = "VB"       #Verb, base form
VBD = "VBD"     #Verb, past tense
VBG = "VBG"     #Verb, gerund or present participle
VBN = "VBN"     #Verb, past participle
VBP = "VBP"     #Verb, non-3rd person singular present
VBZ = "VBZ"     #Verb, 3rd person singular present
VERB_POS = [VB,VBD,VBP,VBZ,VBN] # all types of verb pos
gerund_pos = [VBG]
TO = "TO"
IN = "IN"
MD = "MD"
DOT = "."
COMMA = ","
#pos which will not be needed to cover
ignore_pos = [DOT,COMMA]
relative_adj_pos = ["JJR","JJS"]
relative_adj_words = ["some","other","own",]


#conversion from Penn notation to wordnet notation for lemmatizer
pos_penn_to_wordnet = dict([(vb,'v') for vb in VERB_POS])

def aux_children_with_pos(pos_tag):
    return (lambda node: node.get_pos() == pos_tag and node.get_parent_relation() in aux_dependencies)

##### Tense #####
TENSE_PAST = "past"
TENSE_PRESENT = "present"
TENSE_FUTURE = "future"
TENSE_UNKNOWN = "unknown"

WILL = "will"
WONT = "wo"
WOULD = "would"
ll = "'ll"
D = "'d"
HAVE = "have"
BE = "be"
BEEN = "been"

FUTURE_MODALS = [WILL, WONT, WOULD, ll, D, "may", "might"] # "wo" is the Modal part of "won't"
FUTURE_Signs = ["going", "about"]
#PREP

AS = "as"

#conditionals
COND_IF = "if"
COND_AFTER = "after"
# comparators for DepTree._get_span_of_filtered_children() method

TO_child_func = aux_children_with_pos(TO)
VB_child_func = aux_children_with_pos(VB)
VBD_child_func = aux_children_with_pos(VBD)
VBN_child_func = aux_children_with_pos(VBN)
VBP_child_func = aux_children_with_pos(VBP)
VBP_or_VBZ_child_func = lambda node: (node.get_pos() == VBP or node.get_pos() == VBZ) and node.get_parent_relation() in aux_dependencies
VBD_or_VBN_child_func = lambda node: (node.get_pos() == VBD or node.get_pos() == VBN) and node.get_parent_relation() in aux_dependencies
FUTURE_MD_child_func = lambda node: node.get_pos() == MD and node.get_parent_relation() in aux_dependencies and node.get_word().lower() in FUTURE_MODALS
VB_have_child_func = lambda node: node.get_pos() == VB and node.get_parent_relation() in aux_dependencies and node.get_word().lower() == HAVE
VB_be_child_func = lambda node: node.get_pos() == VB and node.get_parent_relation() in aux_dependencies and node.get_word().lower() == BE
VBN_been_child_func = lambda node: node.get_pos() == VBN and node.get_parent_relation() in aux_dependencies and node.get_word().lower() == BEEN
prep_as_child_func = lambda node: node.get_pos() == IN and node.get_parent_relation() in prepositions_dependencies and node.get_word().lower() == AS
adverb_child_func = lambda node: node.get_parent_relation() in adverb_dependencies
##### Tense - End #####

# copular
copular_verbs = ["be", "am", "is", "are", "being", "was", "were", "been","'s","'re","become","became","becomes"]
modal_list = ["may","might","must","shall","should"]
time_prep = ["at","in","on"]
location_prep = ["at","in","on","of"]
negating_words = ["not","no"]

# conditional marks
condition_outcome_markers = ["if","although","where","after","before","as","until","unless"]
reason_outcome_markers = ["because"]
comp_markers = ["whether"]

contractions = ["'m","'re","'ve","'s"]
