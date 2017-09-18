# Usage:
#     run_pipeline <raw input file>
# Run the Stanford parser over raw sentences file (one per line)
# Following by an invokation of PropS over the json output
# Note:
#   * This assumes that CORENLP_HOME points to the corenlp home directory (containing all jars)
#   * We use the Stanford dependency format (not Universal Dependencies)
#   * We use the makeCopulaHead flag
set -e
# Run Stanford parser
java -cp "$CORENLP_HOME/*" -Xmx2g edu.stanford.nlp.pipeline.StanfordCoreNLP \
    -annotators tokenize,ssplit,pos,parse \
    -file $1 \
    -outputFormat json \
    -parse.originalDependencies -parse.flags " -makeCopulaHead"

# Run PropS on output
# (Stanford outputs to ${1}.json)
# TODO: Stanford doesn't seem to allow printing to standard output, so piping wasn't possible
