import argparse
import sys
import os
from typing import Optional

from .cover_letter import CoverLetterGenerator


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the command line argument parser.
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        description="Generate professional cover letters using AI",
        prog="cover-me",
        epilog="Examples:\n  python -m src.main --file job_description.txt\n  python -m src.main --clipboard\n  python -m src.main -c --preview"
    )
    
    # Input group - mutually exclusive
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "-f", "--file",
        type=str,
        help="Path to file containing job description"
    )
    input_group.add_argument(
        "-c", "--clipboard",
        action="store_true",
        help="Read job description from clipboard"
    )
    
    # Output options
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output file path (optional, defaults to timestamped PDF in output/)"
    )
    
    # Verbosity
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    # Preview mode (for future phases)
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Preview the cover letter without saving (display only)"
    )
    
    return parser


def validate_inputs(args: argparse.Namespace) -> None:
    """Validate command line arguments and required files.
    
    Args:
        args: Parsed command line arguments
        
    Raises:
        SystemExit: If validation fails
    """
    # Check if job description file exists
    if args.file and not os.path.isfile(args.file):
        print(f"Error: Job description file not found: {args.file}", file=sys.stderr)
        sys.exit(1)
    
    # Validate clipboard input if specified
    if args.clipboard:
        try:
            # Load config to get clipboard settings
            import yaml
            with open("config/config.yaml", 'r') as f:
                config = yaml.safe_load(f)
            
            # Use shared clipboard validation
            from .utils.clipboard import get_and_validate_clipboard, ClipboardError
            get_and_validate_clipboard(config)
            
        except ImportError as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            sys.exit(1)
        except ClipboardError as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error: Failed to access clipboard: {str(e)}", file=sys.stderr)
            print("Clipboard functionality may not be available on this system.", file=sys.stderr)
            sys.exit(1)
    
    # Check if required configuration files exist
    required_files = [
        "config/config.yaml",
        "config/system_prompt.md",
        "config/professional_info.md"
    ]
    
    for file_path in required_files:
        if not os.path.isfile(file_path):
            print(f"Error: Required configuration file not found: {file_path}", file=sys.stderr)
            print("Please ensure all configuration files are properly set up.", file=sys.stderr)
            sys.exit(1)


def setup_environment() -> None:
    """Set up the environment and check for required dependencies.
    
    Raises:
        SystemExit: If environment setup fails
    """
    # Check for .env file
    if not os.path.isfile(".env"):
        print("Warning: .env file not found. Please create one based on .env.example", file=sys.stderr)
        print("You'll need to set your OPENAI_API_KEY and other environment variables.", file=sys.stderr)


def main() -> None:
    """Main CLI entry point."""
    # Parse command line arguments
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        # Setup and validation
        setup_environment()
        validate_inputs(args)
        
        if args.verbose:
            print("Initializing cover letter generator...")
        
        # Initialize the cover letter generator
        generator = CoverLetterGenerator()
        
        if args.verbose:
            if args.file:
                print(f"Loading job description from: {args.file}")
            elif args.clipboard:
                print("Loading job description from clipboard")
        
        # Generate cover letter
        if args.file:
            cover_letter = generator.generate_from_file(
                job_description_path=args.file,
                output_path=args.output if not args.preview else None
            )
        elif args.clipboard:
            cover_letter = generator.generate_from_clipboard(
                output_path=args.output if not args.preview else None
            )
        
        # Display results
        if args.preview:
            print("\n" + "="*60)
            print("COVER LETTER PREVIEW")
            print("="*60)
            print(cover_letter)
            print("="*60)
        else:
            print("\n✓ Cover letter generated successfully!")
            if args.output:
                print(f"✓ Saved to: {args.output}")
            else:
                # The generator saves with timestamp, let's show where
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_dir = "output"  # from config
                
                # Determine file extension based on output format
                try:
                    import yaml
                    with open("config/config.yaml", 'r') as f:
                        config = yaml.safe_load(f)
                    output_format = config.get("output", {}).get("format", "text")
                    extension = "pdf" if output_format == "pdf" else "txt"
                except:
                    extension = "txt"  # fallback
                
                estimated_path = os.path.join(output_dir, f"cover_letter_{timestamp}.{extension}")
                print(f"✓ Saved to: {estimated_path}")
        
        if args.verbose:
            print("✓ Process completed successfully")
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(1)
    
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()