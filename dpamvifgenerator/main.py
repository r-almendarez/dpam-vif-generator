import argparse

from dpamvifgenerator import buildinfo, gui, script


def main():
    # Setup command line interface as an alternative to GUI
    parser = argparse.ArgumentParser(buildinfo.__product__)
    parser.add_argument(
        "-i", "--input", dest="in_vif", help="Path to an existing USB VIF XML file"
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="out_vif",
        help="Path and filename for generated output VIF",
    )
    parser.add_argument(
        "-s", "--settings", dest="settings", help="Path to an existing settings.xml"
    )
    parser.add_argument(
        "-b",
        "--batch",
        dest="batch",
        action="store_true",
        help="Run tool in batch mode without launching GUI",
    )
    # Parse args if they exist
    args = parser.parse_args()
    if args.batch:
        script.main(**vars(args))
    else:
        gui.main(**vars(args))


if __name__ == "__main__":
    main()
