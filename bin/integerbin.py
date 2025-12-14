#!/usr/bin/env python3
"""
Splunk custom search command to convert integer fields to binary representation.

Usage:
    | integerbin field=<sourcefield> [output=<destfield>] [prefix=<prefix>]

Examples:
    | integerbin field=status_code
    | integerbin field=port output=port_binary
    | integerbin field=value output=binary_value prefix=0b
"""

import sys
import logging
from typing import Iterator, Dict, Any

from splunklib.searchcommands import (
    dispatch, 
    StreamingCommand, 
    Configuration, 
    Option, 
    validators
)


# Set up logging for debugging
logger = logging.getLogger(__name__)


@Configuration()
class IntegerBinCommand(StreamingCommand):
    """
    Convert integer field values to binary string representation.
    
    This command takes a field containing integer values and produces
    a new field with the binary representation of those integers.
    """
    
    field = Option(
        doc='Source field containing integer values to convert',
        require=True,
        validate=validators.Fieldname()
    )
    
    output = Option(
        doc='Destination field name for binary output (default: binary_output)',
        require=False,
        default='binary_output',
        validate=validators.Fieldname()
    )
    
    prefix = Option(
        doc='Optional prefix for binary output (e.g., "0b")',
        require=False,
        default=''
    )
    
    def stream(self, events: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        """
        Process each event and convert specified field to binary.
        
        Args:
            events: Iterator of event dictionaries from Splunk
            
        Yields:
            Modified event dictionaries with binary field added
        """
        for event in events:
            # Skip events that don't have the source field
            if self.field not in event:
                logger.debug(f"Field '{self.field}' not found in event, skipping")
                yield event
                continue
            
            try:
                binary_value = self._convert_to_binary(event[self.field])
                event[self.output] = f"{self.prefix}{binary_value}"
                
            except ValueError as e:
                # Log the error but continue processing
                logger.warning(
                    f"Failed to convert field '{self.field}' value "
                    f"'{event[self.field]}' to binary: {e}"
                )
                # Optionally add an error field to the event
                event[f"{self.output}_error"] = str(e)
                
            except Exception as e:
                # Log unexpected errors
                logger.error(
                    f"Unexpected error processing event: {e}",
                    exc_info=True
                )
                event[f"{self.output}_error"] = f"Unexpected error: {e}"
            
            yield event
    
    def _convert_to_binary(self, value: Any) -> str:
        """
        Convert a value to binary string representation.
        
        Args:
            value: Value to convert (will be cast to int)
            
        Returns:
            Binary string representation without '0b' prefix
            
        Raises:
            ValueError: If value cannot be converted to integer
        """
        try:
            # Convert to int first to handle string integers and floats
            int_value = int(value)
            
            # Handle negative numbers
            if int_value < 0:
                raise ValueError(
                    f"Cannot convert negative number {int_value} to "
                    f"unsigned binary representation"
                )
            
            # Use format() for clean binary conversion
            return format(int_value, 'b')
            
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Cannot convert '{value}' to integer: {e}"
            ) from e


def main():
    """Entry point for the Splunk search command."""
    dispatch(IntegerBinCommand, sys.argv, sys.stdin, sys.stdout, __name__)


if __name__ == '__main__':
    main()