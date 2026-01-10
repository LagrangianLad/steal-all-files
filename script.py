#!/usr/bin/env python
# -*- coding: utf-8 -*-
PATH = "default"
OUTPUT = "default"
MODE = "w"
# This is the main script of the steal-all-files github repository.
#
# This script has been created by Pablo Corbalán De Concepión
#
# You can read the License for this script in the "LICENSE" file of this folder.
#
# For more information, visit: github.com/HomeomorphicHooligan/steal-all-files (if you have access to it)
from rich.markdown import Markdown
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, FileSizeColumn, TimeRemainingColumn
from rich.table import Table
from rich import box

import sys
import os
import zipfile
import platform

console = Console()

def exitapp(**kwargs):
    """
    This function is used to exit the app using the sys.exit function

    Parameters
    ----------
    kwargs: **
        Some keywords for closing the app
        {
            code: int
                The exit code
            msg: str
                The message if there is a message
        }
    """
    # check if the user has actually used keywords
    keys = kwargs.keys()
    if "msg" in keys:
        k = kwargs["msg"]
        console.print(f"[red]✗[/red] {k}")
    code = 0 if "code" not in keys else kwargs["code"]
    sys.exit(code)



def readfile(file_route):
    """
    Reads a file, handles it's exceptions and then returns the content of
    that file.

    Parameters
    ----------
    file_route: str
        The file route for reading all 

    Returns
    -------
    The content of file_route
    """
    try:
        with open(file_route, encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError as e:
        console.print(Panel(
            f"[red]File Not Found Error[/red]\n\n"
            f"The file '[bold]{file_route}[/bold]' could not be located.\n"
            f"Please ensure the file exists in the current directory.\n\n"
            f"[dim]Error details: {str(e)}[/dim]",
            title="[red]Error[/red]",
            border_style="red",
            box=box.ROUNDED
        ))
        exitapp(code=-1, msg=f"File not found: {file_route}")
    except Exception as e:
        console.print(Panel(
            f"[red]File Reading Error[/red]\n\n"
            f"An unexpected error occurred while reading '[bold]{file_route}[/bold]'.\n\n"
            f"[dim]Error details: {str(e)}[/dim]",
            title="[red]Error[/red]",
            border_style="red",
            box=box.ROUNDED
        ))
        exitapp(code=-1, msg=f"Error reading file: {file_route}")



def displayhelp():
    """
    This function is used for displaying help and the commands about the application

    For running this function use: -h
    """
    f = readfile("help.txt")
    console.print(Panel(
        f,
        title="[cyan]Help[/cyan]",
        border_style="cyan",
        box=box.ROUNDED,
        padding=(1, 2)
    ))



def displaylicense():
    """
    This function is used for displaying the License of this app.

    For running this function use: -l
    """
    f = readfile("LICENSE.md")
    console.print(Markdown(f))



def systemis(system_to_check):
    """
    Get's the system (os) and returns True if the system is
    :param system_to_check:

    Parameters
    ----------
    system_to_check: str
        The system that has to be checked
    
    Returns true if the system to be checked is the actual os
    """
    system = platform.system().lower()
    return True if system == system_to_check else False



def setuppath():
    """
    Set's up the path depending on the operative system the user is using.
    """
    global PATH
    if PATH == "default":
        PATH = "C:\\" if systemis("windows") else "/"



def setupoutput():
    """
    Set's up the output depending on the path
    """
    global OUTPUT, PATH
    if OUTPUT == "default":
       # Use the computer name as the output filename, as per README
       computer_name = platform.node()
       OUTPUT = f"{computer_name}.zip"



def zipdir(path, ziph, progress=None):
    """
    This is the function that actually walks the directory and extracts the files
    inside a ZipFile using the zipfile library.

    Parameters
    ----------
    path: str
        The relative or absolute path for the directory
    ziph: zipfile.ZipFile
        The zipfile handler
    progress: Progress
        Rich progress bar for showing file processing status
    """
    file_count = 0
    skipped_count = 0
    total_size = 0
    
    # First pass: count files for progress tracking
    for root, dirs, files in os.walk(path):
        file_count += len(files)
    
    task = None
    if progress:
        task = progress.add_task("[cyan]Compressing files...", total=file_count)
    
    current_file = 0
    for root, dirs, files in os.walk(path):
        for file in files:
            current_file += 1
            try:
                f = os.path.join(root, file)
                # Use the path relative to the root path being zipped
                arcname = os.path.relpath(f, path)
                
                # Get file size for progress
                try:
                    file_size = os.path.getsize(f)
                    total_size += file_size
                except:
                    file_size = 0
                
                ziph.write(f, arcname)
                
                if progress and task is not None:
                    progress.update(task, advance=1, description=f"[cyan]Processing:[/cyan] {os.path.basename(f)}")
            except (PermissionError, OSError, IOError) as e:
                skipped_count += 1
                # Skip files that can't be read (permission denied, locked files, etc.)
                if progress:
                    progress.console.print(f"[yellow]⚠[/yellow] [dim]Skipped (permission denied):[/dim] {f}")
                else:
                    console.print(f"[yellow]⚠[/yellow] [dim]Skipped (permission denied):[/dim] {f}")
                if task is not None:
                    progress.update(task, advance=1)
            except Exception as e:
                skipped_count += 1
                # Skip any other unexpected errors
                if progress:
                    progress.console.print(f"[yellow]⚠[/yellow] [dim]Skipped (error):[/dim] {f} - {str(e)}")
                else:
                    console.print(f"[yellow]⚠[/yellow] [dim]Skipped (error):[/dim] {f} - {str(e)}")
                if task is not None:
                    progress.update(task, advance=1)
    
    return file_count, skipped_count, total_size



def isarg(arg, value=False):
    """
    Returns True if the argument :arg: is an actual argument

    Parameters
    ----------
    arg: str
        The argument to be checked
    value: bool
        True if :arg: should have a value
    """
    is_arg = False
    arg_value = None
    args = sys.argv
    if not value:
        if arg in args:
            is_arg = True
    else:
        # We also have to check if the argument has a value to then return it
        for i, argument in enumerate(args):
            if argument == arg:
                if i + 1 < len(args):
                    arg_value = args[i + 1]
                    is_arg = True
    # Return a tupple with all this information
    return (is_arg, arg_value)



def readargs():
    """
    This function reads the arguments of the application using the system library to 
    display them and set up the global configuration variables using :func isarg:

    This function does'nt take any parameters nor returns any value
    """
    global PATH, OUTPUT
    # Check out the flags
    if isarg("-h")[0]:
        # The user simply wants to display some help and information about the program
        displayhelp()
        exitapp()
    if isarg("-l")[0]:
        displaylicense()
        exitapp()
    if isarg("-p", True)[0]:
        path_value = isarg("-p", True)[1]
        if path_value is None or path_value.startswith("-"):
            console.print(Panel(
                "[red]Invalid Argument: -p[/red]\n\n"
                "The [bold]-p[/bold] option requires a path value.\n"
                "Usage: [bold]python script.py -p <path>[/bold]\n\n"
                "Example: [bold]python script.py -p C:\\Users\\Documents[/bold]",
                title="[red]Error[/red]",
                border_style="red",
                box=box.ROUNDED
            ))
            exitapp(code=1, msg="Invalid usage: -p requires a path argument")
        PATH = path_value
    if isarg("-o", True)[0]:
        o = isarg("-o", True)[1]
        if o is None or o.startswith("-"):
            console.print(Panel(
                "[red]Invalid Argument: -o[/red]\n\n"
                "The [bold]-o[/bold] option requires an output filename value.\n"
                "Usage: [bold]python script.py -o <output_name>[/bold]\n\n"
                "Example: [bold]python script.py -o my_backup[/bold]\n"
                "This will create [bold]my_backup.zip[/bold]",
                title="[red]Error[/red]",
                border_style="red",
                box=box.ROUNDED
            ))
            exitapp(code=1, msg="Invalid usage: -o requires an output filename argument")
        OUTPUT = f"{o}.zip"
    if isarg("-rw")[0]:
        # Note: -rw flag is documented but the functionality for removing write permissions
        # would need to be implemented after ZIP creation using os.chmod on Unix systems
        # For now, this flag doesn't affect the ZIP creation mode
        pass



if __name__ == "__main__":
    # Display startup banner
    console.print(Panel.fit(
        "[bold cyan]Steal All Files[/bold cyan]\n"
        "[dim]Cybersecurity Tool - File Extraction Utility[/dim]",
        border_style="cyan",
        box=box.DOUBLE
    ))
    console.print()
    
    setuppath()
    setupoutput()
    readargs()
    # Ensure MODE is set to a valid value
    if MODE == "":
        MODE = "w"
    
    # Display configuration table
    config_table = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
    config_table.add_column("Setting", style="cyan", no_wrap=True)
    config_table.add_column("Value", style="green")
    
    config_table.add_row("Source Path", PATH)
    config_table.add_row("Output File", OUTPUT)
    config_table.add_row("Operating System", platform.system())
    config_table.add_row("Computer Name", platform.node())
    
    console.print(Panel(
        config_table,
        title="[cyan]Configuration[/cyan]",
        border_style="cyan",
        box=box.ROUNDED
    ))
    console.print()
    
    # Validate that PATH exists and is accessible
    if not os.path.exists(PATH):
        console.print(Panel(
            f"[red]Path Not Found[/red]\n\n"
            f"The specified path '[bold]{PATH}[/bold]' does not exist.\n"
            f"Please verify the path and try again.",
            title="[red]Error[/red]",
            border_style="red",
            box=box.ROUNDED
        ))
        exitapp(code=1, msg=f"Path not found: {PATH}")
    if not os.path.isdir(PATH):
        console.print(Panel(
            f"[red]Invalid Path Type[/red]\n\n"
            f"The path '[bold]{PATH}[/bold]' exists but is not a directory.\n"
            f"Please specify a valid directory path.",
            title="[red]Error[/red]",
            border_style="red",
            box=box.ROUNDED
        ))
        exitapp(code=1, msg=f"Not a directory: {PATH}")
    
    console.print(Panel(
        f"[bold]Starting compression process...[/bold]\n\n"
        f"Source: [cyan]{PATH}[/cyan]\n"
        f"Output: [cyan]{OUTPUT}[/cyan]\n\n"
        f"[dim]Press CTRL+C to cancel the operation[/dim]",
        title="[green]Ready[/green]",
        border_style="green",
        box=box.ROUNDED
    ))
    console.print()
    
    try:
        z = None
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            FileSizeColumn(),
            TimeRemainingColumn(),
            console=console,
            transient=False
        ) as progress:
            z = zipfile.ZipFile(OUTPUT, MODE, zipfile.ZIP_DEFLATED)
            file_count, skipped_count, total_size = zipdir(PATH, z, progress)
            z.close()
        
        # Calculate output file size
        output_size = os.path.getsize(OUTPUT) if os.path.exists(OUTPUT) else 0
        
        # Display success summary
        summary_table = Table(show_header=True, header_style="bold green", box=box.ROUNDED)
        summary_table.add_column("Metric", style="cyan", no_wrap=True)
        summary_table.add_column("Value", style="green", justify="right")
        
        summary_table.add_row("Files Processed", f"{file_count:,}")
        summary_table.add_row("Files Skipped", f"{skipped_count:,}")
        summary_table.add_row("Files Added", f"{file_count - skipped_count:,}")
        summary_table.add_row("Output File Size", f"{output_size / (1024*1024):.2f} MB")
        
        console.print()
        console.print(Panel(
            summary_table,
            title="[green]✓ Operation Completed Successfully[/green]",
            border_style="green",
            box=box.ROUNDED
        ))
        console.print()
        console.print(f"[bold green]✓[/bold green] Archive created successfully: [cyan]{OUTPUT}[/cyan]")
        
        if skipped_count > 0:
            console.print(f"[yellow]⚠[/yellow] [dim]{skipped_count} file(s) were skipped due to permissions or errors[/dim]")
        
    except KeyboardInterrupt:
        console.print()
        console.print(Panel(
            "[yellow]Operation Cancelled[/yellow]\n\n"
            "The compression process was interrupted by the user.\n"
            "Any partially created files may remain.",
            title="[yellow]Interrupted[/yellow]",
            border_style="yellow",
            box=box.ROUNDED
        ))
        if 'z' in locals() and z is not None:
            z.close()
            # Try to remove incomplete file
            if os.path.exists(OUTPUT):
                try:
                    os.remove(OUTPUT)
                    console.print(f"[dim]Cleaned up incomplete file: {OUTPUT}[/dim]")
                except:
                    pass
        sys.exit(1)
    except zipfile.BadZipFile as e:
        console.print(Panel(
            f"[red]ZIP File Error[/red]\n\n"
            f"An error occurred while creating the ZIP archive.\n"
            f"The output file may be corrupted.\n\n"
            f"[dim]Error details: {str(e)}[/dim]",
            title="[red]Error[/red]",
            border_style="red",
            box=box.ROUNDED
        ))
        if 'z' in locals() and z is not None:
            z.close()
        sys.exit(1)
    except Exception as e:
        console.print(Panel(
            f"[red]Unexpected Error[/red]\n\n"
            f"An unexpected error occurred during the compression process.\n\n"
            f"[dim]Error details: {str(e)}[/dim]",
            title="[red]Error[/red]",
            border_style="red",
            box=box.ROUNDED
        ))
        if 'z' in locals() and z is not None:
            z.close()
        sys.exit(1)
