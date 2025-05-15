#!/usr/bin/env python
"""Generate API documentation for the Mail Scheduler application."""
import os
import subprocess
import sys


def main():
    """Run the main documentation generation process."""
    project_root = os.path.dirname(os.path.abspath(__file__))
    docs_dir = os.path.join(project_root, "docs")

    print("Generating API documentation...")

    # Check and install required dependencies
    try:
        # Check if required packages are installed
        try:
            __import__("sphinx")
            __import__("sphinx_rtd_theme")
            __import__("sphinxcontrib.httpdomain")
        except ImportError:
            print("Installing required documentation dependencies...")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "sphinxcontrib-httpdomain"],
                check=True,
            )
    except ImportError:
        print("Installing required documentation dependencies...")
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "sphinx",
                "sphinx-rtd-theme",
                "sphinxcontrib-httpdomain",
            ],
            check=True,
        )

    # Ensure docs directory exists
    if not os.path.exists(docs_dir):
        print(f"Creating docs directory at {docs_dir}")
        os.makedirs(os.path.join(docs_dir, "source"), exist_ok=True)
        os.makedirs(os.path.join(docs_dir, "build"), exist_ok=True)

    # Generate documentation using Sphinx
    build_command = ["make", "html"]
    print(f"Running: {' '.join(build_command)} in {docs_dir}")

    try:
        os.chdir(docs_dir)
        subprocess.run(build_command, check=True)

        # Print success message and location of docs
        html_dir = os.path.join(docs_dir, "build", "html")
        print("\nDocumentation generated successfully!")
        print(f"HTML documentation is available at: {html_dir}")
        print("To view the documentation in your browser:")
        print(f"  file://{html_dir}/index.html")

        # Optional: Open the docs in the default web browser
        if len(sys.argv) > 1 and sys.argv[1] == "--open":
            import webbrowser

            webbrowser.open(f"file://{html_dir}/index.html")

        return 0
    except subprocess.CalledProcessError as e:
        print(f"Error generating documentation: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
