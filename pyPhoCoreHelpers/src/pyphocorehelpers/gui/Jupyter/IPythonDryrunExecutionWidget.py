import asyncio
from time import time
from threading import Timer # used in `throttle(...)`
from pyphocorehelpers.programming_helpers import metadata_attributes
from pyphocorehelpers.function_helpers import function_attributes
from enum import Enum
import ipywidgets as widgets
from IPython.display import display

class DryRunExecutionWidget:
    """A widget that executes a function in dry-run mode first and provides a button 
    to execute it for real, handling verbose output appropriately.

    Usage:
    ------
    # Define the function that takes is_dryrun parameter
    def my_operation(is_dryrun=True):
        copy_dict, moved_files_dict_files = AcrossSessionHelpers._copy_exported_files_from_session_folder_to_collected_outputs(
            BATCH_DATE_TO_USE=BATCH_DATE_TO_USE, 
            cuttoff_date=cuttoff_date, 
            target_dir=collected_outputs_directory, 
            custom_file_globs_dict={'h5': '*.h5'}, 
            is_dry_run=is_dryrun
        )
        return (copy_dict, moved_files_dict_files)

    # Create and use the widget
    widget = DryRunExecutionWidget(my_operation)
    """

    def __init__(self, operation_function, execute_button_label="Execute for Real (Non-dry run)", output_max_height="200px", capture_prints=True, show_return_value=True):
        """Initialize the widget.

        Parameters:
        -----------
        operation_function : callable
            A function that takes an is_dryrun parameter and returns results
        execute_button_label : str
            Label for the execute button
        output_max_height : str
            Maximum height for output areas
        capture_prints : bool
            Whether to capture print statements (set to False if function is very verbose)
        show_return_value : bool
            Whether to display the return value of the function
        """
        import ipywidgets as widgets
        from IPython.display import display

        self.operation_function = operation_function
        self.capture_prints = capture_prints
        self.show_return_value = show_return_value

        # Create control panel with fixed position
        self.control_panel = widgets.VBox([
            widgets.HTML("<h3>Dry Run Execution Controls</h3>"),
            widgets.HTML("<p>Preview what will happen without making changes</p>")
        ])

        # Create the execute button (with fixed position)
        self.execute_button = widgets.Button(
            description=execute_button_label,
            button_style='danger',
            tooltip='Execute the operation for real (not a dry run)',
            icon='exclamation-triangle',
            layout=widgets.Layout(width='300px', margin='10px 0')
        )

        # Add button to control panel
        self.control_panel.children = (*self.control_panel.children, self.execute_button)

        # Create status display
        self.status = widgets.HTML(
            value="<b>Status:</b> Previewing in dry run mode",
            layout=widgets.Layout(margin='10px 0')
        )

        # Add status to control panel
        self.control_panel.children = (*self.control_panel.children, self.status)

        # Improve container for preview results with better scrolling behavior
        self.preview_area = widgets.Output(
            layout=widgets.Layout(
                border='1px solid #ddd',
                padding='10px',
                margin='10px 0',
                max_height=output_max_height,
                overflow_y='auto',
                overflow_x='auto',  # Add horizontal scrolling too
                width='100%',       # Ensure it takes full width
                flex_flow='column', # Stack content vertically
                display='flex'      # Use flex display
            )
        )

        # Container for real execution results with better scrolling
        self.execution_area = widgets.Output(
            layout=widgets.Layout(
                border='1px solid #ddd',
                padding='10px',
                margin='10px 0',
                max_height=output_max_height,
                overflow_y='auto',
                overflow_x='auto',  # Add horizontal scrolling too
                width='100%',       # Ensure it takes full width
                flex_flow='column', # Stack content vertically
                display='flex'      # Use flex display
            )
        )

        def on_execute_button_clicked(_):
            self._execute_for_real()

        self.execute_button.on_click(on_execute_button_clicked)

        # Create header labels
        self.preview_header = widgets.HTML("<h4>Dry Run Preview:</h4>")
        self.execution_header = widgets.HTML("<h4>Real Execution Results:</h4>")

        # Create the widget UI - put controls in a separate fixed box
        self.control_box = widgets.Box([self.control_panel],
            layout=widgets.Layout(
                border='1px solid #ccc',
                padding='10px',
                margin='10px 0',
                background_color='#f8f8f8'
            )
        )

        self.output_box = widgets.VBox([
            self.preview_header,
            self.preview_area,
            self.execution_header,
            self.execution_area
        ])

        self.widget = widgets.VBox([
            self.control_box,
            self.output_box
        ])

        # Execute in dry run mode immediately
        self._execute_dry_run()

        # Display the widget
        display(self.widget)

    def _capture_output(self, func, *args, **kwargs):
        """Capture output from a function if requested."""
        import io
        import sys
        from contextlib import redirect_stdout, redirect_stderr

        if self.capture_prints:
            # Capture stdout and stderr
            f = io.StringIO()
            with redirect_stdout(f), redirect_stderr(f):
                result = func(*args, **kwargs)
            output = f.getvalue()
            return result, output
        else:
            # Don't capture, just run the function
            result = func(*args, **kwargs)
            return result, None

    def _execute_dry_run(self):
        """Execute the operation in dry run mode."""
        try:
            self.status.value = "<b>Status:</b> Running dry run preview..."

            # Clear previous preview
            self.preview_area.clear_output()

            # Execute the function with is_dryrun=True
            with self.preview_area:
                from IPython.display import display, HTML
                print("Dry run preview (no actual changes made)...")

                result, output = self._capture_output(self.operation_function, is_dryrun=True)

                if output and self.capture_prints:
                    print("\n--- Function output: ---")

                    # Limit output length if it's very large
                    if len(output) > 50000:  # Limit to ~50KB of text
                        truncated_output = output[:25000] + "\n\n... [OUTPUT TRUNCATED] ...\n\n" + output[-25000:]
                        print(truncated_output)
                    else:
                        # Wrap the output in a pre tag with specific styling for scrolling
                        html_output = f"""<pre style="max-height: {self.preview_area.layout.max_height}; 
                                               overflow-y: auto; 
                                               white-space: pre-wrap; 
                                               word-break: break-all;">{output}</pre>"""
                        display(HTML(html_output))

                if self.show_return_value:
                    print("\n--- Return value: ---")
                    display(result)

            self.status.value = "<b>Status:</b> Dry run preview completed"

        except Exception as e:
            self.status.value = f"<b>Status:</b> Error during dry run: {str(e)}"
            with self.preview_area:
                import traceback
                print(f"Error during dry run: {str(e)}")
                traceback.print_exc()


    def _execute_for_real(self):
        """Execute the operation for real (non-dry run)."""
        try:
            self.status.value = "<b>Status:</b> Executing for real..."
            self.execute_button.disabled = True

            # Clear previous execution results
            self.execution_area.clear_output()

            # Execute the function with is_dryrun=False
            with self.execution_area:
                from IPython.display import display
                print("Executing operation for real...")

                result, output = self._capture_output(self.operation_function, is_dryrun=False)

                if output and self.capture_prints:
                    print("\n--- Function output: ---")
                    print(output)

                if self.show_return_value:
                    print("\n--- Return value: ---")
                    display(result)

                print("\nReal execution completed.")

            self.status.value = "<b>Status:</b> Real execution completed"

        except Exception as e:
            self.status.value = f"<b>Status:</b> Error during real execution: {str(e)}"
            with self.execution_area:
                import traceback
                print(f"Error during real execution: {str(e)}")
                traceback.print_exc()
        finally:
            self.execute_button.disabled = False
