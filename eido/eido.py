import logging
import os
import jsonschema
import oyaml as yaml

import logmuse
from ubiquerg import VersionInHelpParser
from peppy import Project

from . import __version__
from .const import *

_LOGGER = logging.getLogger(__name__)


def build_argparser():
    banner = "%(prog)s - validate project metadata against a schema"
    additional_description = "\nhttps://github.com/pepkit/eido"

    parser = VersionInHelpParser(
            prog=PKG_NAME,
            description=banner,
            epilog=additional_description)

    parser.add_argument(
            "-V", "--version",
            action="version",
            version="%(prog)s {v}".format(v=__version__))

    parser.add_argument(
            "-p", "--pep", required=True,
            help="PEP configuration file in yaml format.")

    parser.add_argument(
            "-s", "--schema", required=True,
            help="PEP schema file in yaml format.")

    return parser


def load_yaml(filepath):
    """
    Read a YAML file

    :param str filepath: path to the file to read
    :return dict: read data
    """
    with open(filepath, 'r') as f:
        data = yaml.safe_load(f)
    return data


def validate_pep(p, schema):
    """
    Validate a project object against a schema

    :param peppy.Project p: a project object to validate
    :param str | dict schema: schema dict to validate against or a path to one
    :return:
    """
    if isinstance(schema, str) and os.path.isfile(schema):
        schema_dict = load_yaml(schema)
    elif isinstance(schema, dict):
        schema_dict = schema
    else:
        raise TypeError("schema has to be either a dict or a path to an existing file")
    p_dict = p.to_dict()
    jsonschema.validate(p_dict, schema_dict)


def main():
    """ Primary workflow """
    parser = logmuse.add_logging_options(build_argparser())
    args, remaining_args = parser.parse_known_args()
    logger_kwargs = {"level": args.verbosity, "devmode": args.logdev}
    logmuse.init_logger(name="peppy", **logger_kwargs)
    logmuse.init_logger(name=PKG_NAME, **logger_kwargs)
    global _LOGGER
    _LOGGER = logmuse.logger_via_cli(args)
    p = Project(args.pep)
    _LOGGER.debug("Comparing PEP ('{}') against schema: {}.".format(args.pep, args.schema))
    validate_pep(p, args.schema)
    _LOGGER.info("Validation successful")
