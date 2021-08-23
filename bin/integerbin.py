import sys
from splunklib.searchcommands import \
    dispatch, StreamingCommand, Configuration, Option

@Configuration()
class integerbin(StreamingCommand):
    """
    Take a source field as an unsigned int
    Produce an equivalent output field as a binary digit
     | integerbin field=<sourcefield>   
    """
    field = Option(name='field', require=True)
    def stream(self, events):
        for event in events:
            if not self.field in event:
                continue
            try:
                dest_field = "binary_output"

                # format() doesn't like it if the field is formatted as str()
                # already, hence that's the reason for the int() function

                binary_result = format(int(event[self.field]), "b")
                event[dest_field] = binary_result
            except Exception as e:
                raise e
            yield event

dispatch(integerbin, sys.argv, sys.stdin, sys.stdout, __name__)
