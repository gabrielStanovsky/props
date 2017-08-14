<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [GeoQuery Analysis](#geoquery-analysis)
  - [Wh-questions](#wh-questions)
    - [Examples (Conll output representation)](#examples-conll-output-representation)
  - ["Imperative" questions](#imperative-questions)
    - [Examples (sentences)](#examples-sentences)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# GeoQuery Analysis

GeoQuery question type analysis, and the desired respective PropS structures.

## Wh-questions

We posit the Wh-question as the head of the predicate with a single argument, 
labeled with a new 'inquiry' edge label.

### Examples (Conll output representation)

* ```echo "How long is the Colorado River?" | python props/applications/parse_props.py -t --oie```

        How long is the Colorado River ?
        0       2,long  RB      0       0       mod,2
        1       1,How   WRB     1       1
        2       3,is    VBZ     1       0       inquiry,1
        8       5,Colorado;6,River      NNP     0       0       subj,2
        
        How:(inquiry:long is the Colorado River ? )
        


## "Imperative" questions

These seem to be imperative sentences with a question mark added at the end of the sentence.

Not sure how to represent these, since their underlying syntactic analysis will differ from wh-questions.

### Examples (sentences)

* *Give me the number of rivers in california?"*
* *Count the states which have elevations lower than what alabama has?*
