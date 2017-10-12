import click

import guild.click_util

@click.command()
@click.option(
    "-p", "--project", "project_location", metavar="LOCATION",
    help=("Project location (file system directory) of the "
          "project to package. Defaults to current directory."))
@click.option(
    "-d", "--dist-dir", metavar="DIR",
    help="Directory to create the package distribution in.")

@click.pass_context
@guild.click_util.use_args

def package(ctx, args):
    """Create a package for distribution.

    Packages are built from projects that contain a PACKAGE file that
    describes the package to be built.
    """
    import guild.package_cmd_impl
    guild.package_cmd_impl.create_package(args, ctx)
