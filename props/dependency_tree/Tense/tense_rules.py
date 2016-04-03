__author__ = 'user'
from props.dependency_tree.definitions import *

# present - "As a result, U.S. Trust's earnings have been hurt"
def passive_VBN_child(predicate,passive_child):
    if predicate.pos == VBN and passive_child.pos == VBN:
        return (TENSE_PRESENT,(passive_child.id,passive_child.id))

# present - "The debt reduction is expected to save the Fort Lauderdale"
def passive_VBP_VBZ_child(predicate,passive_child):
    if predicate.pos == VBN and passive_child.pos == VBP or passive_child.pos == VBZ:
        return (TENSE_PRESENT,(passive_child.id,passive_child.id))


# past - "was being supported"
# present - "Each note is being offered at $ 308.32 per $1,000 principal amount at maturity"
def passive_VBG_child(predicate,passive_child):

    flag_VBP_VBZ,span_VBP_VBZ,node = predicate._get_span_of_filtered_children(VBP_or_VBZ_child_func)
    flag_VBD_VBN,span_VBD_VBN,node = predicate._get_span_of_filtered_children(VBD_or_VBN_child_func)
    min_VBP_VBZ, max_VBP_VBZ = span_VBP_VBZ
    min_VBD_VBN, max_VBD_VBN = span_VBD_VBN
    if predicate.pos == VBN and passive_child.pos == VBG and passive_child.word.lower() == "being":
        if flag_VBD_VBN:
            return (TENSE_PAST,(min_VBD_VBN,passive_child.id))
        elif flag_VBP_VBZ:
            return (TENSE_PRESENT,(min_VBP_VBZ,passive_child.id))

def passive_VBD_child(predicate,passive_child):
    if predicate.pos == VBN and passive_child.pos == VBD  :
        return (TENSE_PAST,(passive_child.id,passive_child.id))

# future - "The gross will be used to reduce existing debt and for general corporate purposes"
# future - "this opinion is going to be used as a mechanism for ejecting us from the talks"
def passive_VB_child(predicate,passive_child):
    flag_TO,span_TO,node = predicate._get_span_of_filtered_children(TO_child_func)
    flag_FUTURE_MD,span_FUTURE_MD,node = predicate._get_span_of_filtered_children(FUTURE_MD_child_func)
    min_FUTURE_MD, max_FUTURE_MD = span_FUTURE_MD

    if predicate.pos == VBN and passive_child.pos == VB and passive_child.word == BE:
        if flag_FUTURE_MD:
            return (TENSE_FUTURE,(min_FUTURE_MD,passive_child.id))
        if  flag_TO :
            if predicate.get_parent_relation() in clausal_complement and (predicate.parent.word.lower() in FUTURE_Signs):
                return (TENSE_FUTURE,(predicate.parent.word + "to"))
            return (TENSE_FUTURE,("to be"))

# past - "Mr. Stronach resigned last year to seek , unsuccessfully , a seat in Canada 's Parliament"
def infinitives_VBD_parent(predicate):
    if predicate.parent.pos == VBD:
        return (TENSE_PAST,(predicate.parent.word + "to"))

# present - "They expect him to cut costs throughout the organization"
def infinitives_VBP_parent(predicate):
    if predicate.parent.pos == VBP:
        return (TENSE_PRESENT,(predicate.parent.word + "to"))


# future - "The gross will be used to reduce existing debt and for general corporate purposes , the company said"
def infinitives_future(predicate):
    flag_FUTURE_MD,span_FUTURE_MD,node = predicate.parent._get_span_of_filtered_children(FUTURE_MD_child_func)
    if flag_FUTURE_MD:
        return (TENSE_FUTURE,node.word + predicate.parent.word + "to")


# past - "they had already eaten dinner"
def past_VBN_pos(predicate):
    flag_VBD,span_VBD,node = predicate._get_span_of_filtered_children(VBD_child_func)
    if  (predicate.pos == VBN or predicate.pos == VB) and flag_VBD:
            return (TENSE_PAST,span_VBD)

# past - "Tammy had been studying for two hours"
# past - "we were discussing the problem"
def past_VBG_pos(predicate):
    flag_VBD,span_VBD,node = predicate._get_span_of_filtered_children(VBD_child_func)
    flag_VBN,span_VBN,node = predicate._get_span_of_filtered_children(VBN_child_func)
    min_VBD,max_VBD = span_VBD
    min_VBN,max_VBN = span_VBN
    if predicate.pos == VBG  and flag_VBD :
        if flag_VBN:
            return (TENSE_PAST,(min(min_VBD,min_VBN),max(max_VBD,max_VBN)))
        return (TENSE_PAST,span_VBD)

# present - "I have eaten too much" / "I have never been to Europe"
def present_VBN_pos(predicate):
    flag_VBP_or_VBZ,span_VBP_or_VBZ,node = predicate._get_span_of_filtered_children(VBP_or_VBZ_child_func)
    if (predicate.pos == VBN or predicate.pos == VBD) and flag_VBP_or_VBZ:
        return (TENSE_PRESENT,span_VBP_or_VBZ)

# present simple - "Dogs eat once a day"
def present_VBP_pos(predicate):
    if predicate.pos == VBP or predicate.pos == VBZ:
        return (TENSE_PRESENT,(predicate.id,predicate.id))

# present - "I have been studying at the Open University for three years"
# present progressive - "They are calling your name"
def present_VBG_pos(predicate):
    flag_VBP_or_VBZ,span_VBP_or_VBZ,node = predicate._get_span_of_filtered_children(VBP_or_VBZ_child_func)
    min_VBP_or_VBZ,max_VBP_or_VBZ = span_VBP_or_VBZ
    flag_VBN,span_VBN,node = predicate._get_span_of_filtered_children(VBN_child_func)
    min_VBN,max_VBN = span_VBN
    flag_VBP_VBZ,span_VBP_VBZ,node = predicate._get_span_of_filtered_children(VBP_or_VBZ_child_func)
    if predicate.pos == VBG and flag_VBP_or_VBZ and flag_VBN:
        return (TENSE_PRESENT,(min(min_VBP_or_VBZ,min_VBN),max(max_VBP_or_VBZ,max_VBN)))
    if (predicate.pos == VBG or predicate.pos == VB) and flag_VBP_VBZ:
        return (TENSE_PRESENT,span_VBP_VBZ)


# future - "I will help you"
def future_VB_pos(predicate):
    flag_FUTURE_MD,span_FUTURE_MD,node = predicate._get_span_of_filtered_children(FUTURE_MD_child_func)
    flag_TO,span_TO,node = predicate._get_span_of_filtered_children(TO_child_func)
    if predicate.pos == VB and flag_FUTURE_MD:
        return (TENSE_FUTURE,span_FUTURE_MD)
    if predicate.pos == VB and flag_TO and predicate.get_parent_relation() in clausal_complement and (predicate.parent.word.lower() in FUTURE_Signs):
            return (TENSE_FUTURE,True)


# future - "By the end of August I will have finished my studies"
def future_VBN_pos(predicate):
    flag_FUTURE_MD,span_FUTURE_MD,node = predicate._get_span_of_filtered_children(FUTURE_MD_child_func)
    flag_VB_have,span_VB_have,node = predicate._get_span_of_filtered_children(VB_have_child_func)
    min_FUTURE_MD, max_FUTURE_MD = span_FUTURE_MD
    min_VB_have, max_VB_have = span_VB_have
    if predicate.pos == VBN and flag_VB_have and flag_FUTURE_MD:
        return (TENSE_FUTURE,(min_FUTURE_MD,max_VB_have))

# future - "Tomorrow at four I will be flying to Paris"
# future - "By the time you go abroad you will have been studying English for 10 years"
def future_VBG_pos(predicate):
    flag_FUTURE_MD,span_FUTURE_MD,node = predicate._get_span_of_filtered_children(FUTURE_MD_child_func)
    min_FUTURE_MD, max_FUTURE_MD = span_FUTURE_MD
    flag_VB_have,span_VB_have,node = predicate._get_span_of_filtered_children(VB_have_child_func)
    flag_VB_be,span_VB_be,node = predicate._get_span_of_filtered_children(VB_be_child_func)
    min_VB_be, max_VB_be = span_VB_be
    flag_VBN_been,span_VBN_been,node = predicate._get_span_of_filtered_children(VBN_been_child_func)
    min_VBN_been, max_VBN_been = span_VBN_been
    if predicate.pos == VBG and flag_VB_be and flag_FUTURE_MD:
        return (TENSE_FUTURE,(min_FUTURE_MD,max_VB_be))
    if predicate.pos == VBG and flag_VBN_been and flag_FUTURE_MD and flag_VB_have:
        return (TENSE_FUTURE,(min_FUTURE_MD,max_VBN_been))


def simple_rules(predicate):
    if predicate.pos == VBG:
        return (TENSE_PRESENT,True)
    # past - "he watched TV"
    if predicate.pos == VBD or predicate.pos == VBN:
        return (TENSE_PAST,(predicate.id, predicate.id))

###########################################################################################################

infinitives_tense_rules = [infinitives_VBD_parent, infinitives_VBP_parent, infinitives_future ]
active_voice_tense_rules = [past_VBN_pos,past_VBG_pos,present_VBN_pos,present_VBP_pos,present_VBG_pos,future_VB_pos,future_VBN_pos,future_VBG_pos]
passive_voice_tense_rules = [passive_VBN_child,passive_VBP_VBZ_child,passive_VBG_child,passive_VBD_child,passive_VB_child]

############################################################################################################


def get_tense(predicate,run_simple_rules = True):
    span=False
    flag_TO,span_TO,node = predicate._get_span_of_filtered_children(TO_child_func)

    # run passive rules
    passive_nodes = filter(lambda x:x.get_parent_relation() in passive_dependencies, predicate.children)
    if passive_nodes:
        child = passive_nodes[0]
        for f in passive_voice_tense_rules:
            result = f(predicate,child)
            if result:
                return result

    # run infinitives rules
    elif flag_TO  and predicate.get_parent_relation() in clausal_complement and predicate.parent.word.lower() not in FUTURE_Signs:
        for f in infinitives_tense_rules:
            result = f(predicate)
            if result:
                return result

    # run the rest of the rules
    else:
        for f in active_voice_tense_rules:
            result = f(predicate)
            if result:
                return result
        # simple rules - only ny the predicate's POS
        if run_simple_rules:
            result = get_tense_by_simple_rules(predicate)
            if result:
                return result

    return (TENSE_UNKNOWN,span)

def get_tense_by_simple_rules(predicate):
    return simple_rules(predicate)

