"""
Script for initializing new U-Time project directories
"""

from argparse import ArgumentParser
import os


def get_parser():
    """
    Returns an argument parser for this script
    """
    parser = ArgumentParser(description='Create a new project folder')

    # Define groups
    parser._action_groups.pop()
    required = parser.add_argument_group('required named arguments')
    optional = parser.add_argument_group('optional named arguments')
    defaults = os.path.split(__file__)[0] + "/defaults"

    required.add_argument('--name', type=str, required=True,
                        help='the name of the project folder')
    optional.add_argument('--root', type=str, default=os.path.abspath("./"),
                          help='a path to the root folder in '
                               'which the project will be initialized '
                               '(default=./)')
    optional.add_argument("--model", type=str, default="utime",
                          help="Specify a model type parameter file. One of: "
                               "{} (default 'utime')".format(",".join(os.listdir(defaults))))
    optional.add_argument("--data_dir", type=str, default=None,
                          help="Optional specification of path to dir "
                               "storing data")
    return parser


def copy_yaml_and_set_data_dirs(in_path, out_path, data_dir=None):
    """
    Creates a YAMLHParams object from a in_path (a hyperparameter .yaml file),
    inserts the 'data_dir' argument into data_dir fileds in the .yaml file
    (if present) and saves the hyperparameter file to out_path.

    Note: If data_dir is set, it is assumed that the folder contains data in
          sub-folders 'train', 'val' and 'test' (not required to exist).

    args:
        in_path:  (string) Path to a .yaml file storing the hyperparameters
        out_path: (string) Path to save the hyperparameters to
        data_dir: (string) Optional path to a directory storing data to use
                           for this project.
    """
    from utime.hyperparameters import YAMLHParams
    hparams = YAMLHParams(in_path, no_log=True, no_version_control=True)

    # Set values in parameter file and save to new location
    data_ids = ("train", "val", "test")
    for dataset in data_ids:
        path = os.path.join(data_dir, dataset) if data_dir else "Null"
        dataset = dataset + "_data"
        if hparams.get(dataset) and not hparams[dataset].get("data_dir"):
            hparams.set_value(dataset, "data_dir", path, True, True)
    hparams.save_current(out_path)


def init_project_folder(default_folder, preset, out_folder, data_dir=None):
    """
    Create and populate a new project folder with default hyperparameter files.

    Args:
        default_folder: (string) Path to the utime.bin.defaults folder
        preset:         (string) Name of the model/preset directory to use
        out_folder:     (string) Path to the project directory to create and
                                 populate
        data_dir:       (string) Optional path to a directory storing data to
                                 use for this project.
    """
    # Copy files and folders to project dir, set data_dirs if specified
    in_folder = os.path.join(default_folder, preset)
    for dir_path, dir_names, file_names in os.walk(in_folder):
        for dir_name in dir_names:
            p_ = os.path.join(out_folder, dir_name)
            if not os.path.exists(p_):
                os.mkdir(p_)
        for file_name in file_names:
            in_file_path = os.path.join(dir_path, file_name)
            sub_dir = dir_path.replace(in_folder, "").strip("/")
            out_file_path = os.path.join(out_folder, sub_dir, file_name)
            copy_yaml_and_set_data_dirs(in_file_path, out_file_path, data_dir)


def run(args):
    """
    Run this script with the specified args. See argparser for details.
    """
    default_folder = os.path.split(os.path.abspath(__file__))[0] + "/defaults"
    if not os.path.exists(default_folder):
        raise OSError("Default path not found at %s" % default_folder)
    root_path = os.path.abspath(args.root)
    data_dir = args.data_dir
    if data_dir:
        data_dir = os.path.abspath(data_dir)

    # Validate project path and create folder
    if not os.path.exists(root_path):
        raise OSError("root path '{}' does not exist.".format(args.root))
    else:
        out_folder = os.path.join(root_path, args.name)
        if os.path.exists(out_folder):
            response = input("Folder at '{}' already exists. Overwrite? "
                             "Only parameter files will be replaced. "
                             "(y/N) ".format(out_folder))
            if response.lower() != "y":
                raise OSError(
                    "Folder at '{}' already exists".format(out_folder))
        try:
            os.makedirs(out_folder)
        except FileExistsError:
            # Already accepted to overwrite
            pass
    init_project_folder(default_folder, args.model, out_folder, data_dir)


def entry_func(args=None):
    # Parse arguments
    parser = get_parser()
    run(parser.parse_args(args))


if __name__ == "__main__":
    entry_func()
