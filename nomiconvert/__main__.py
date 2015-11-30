import sys

import click

from nomiconvert import convert_v11_v20


@click.command()
@click.option("--from-syntax", required=True, help="Input syntax")
@click.option("--to-syntax", required=True, help="Output syntax")
@click.argument("input", default=None, required=False)
@click.argument("output", default=None, required=False)
def nomi_convert(from_syntax, to_syntax, input, output):
    """
    Convert manifests between different syntaxes.
    """
    syntaxes = {
        ('v1.1', 'v2.0'): convert_v11_v20
    }
    conversion = syntaxes.get((from_syntax, to_syntax))
    if not conversion:
        click.echo("Conversion from %s to %s is not supported. Supported varaints are:" % (from_syntax, to_syntax))
        for (f, t) in syntaxes.keys():
            click.echo("    %s to %s" % (f, t))
        exit(1)
    if input:
        with open(input, "r") as f:
            input_data = f.read()
    else:
        input_data = sys.stdin.read()
    result_data = convert_v11_v20(input_data)
    if output:
        with open(output, "w") as f:
            f.write(result_data)
    else:
        sys.stdout.write(result_data)
        sys.stdout.flush()


