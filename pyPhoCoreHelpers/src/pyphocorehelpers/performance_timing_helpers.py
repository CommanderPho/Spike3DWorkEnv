import time



class WrappingPerformanceTimer(object):
    """ TODO: Doesn't quite work. Doesn't return the contents of its body which it should.
    
    Examples:
        with WrappingPerformanceTimer('Saving 2D Placefield image out to "{}"...'.format(active_plot_filepath), begin_line_ending='...', finished_message='done.'):
            for aFig in active_figures:
                aFig.savefig(active_plot_filepath)
    """
    def __init__(self, begin_string, begin_line_ending=' ', finished_message='done.', finished_line_ending='\n', returns_string:bool=False, enable_print:bool=True):
        self.start_time = time.time()
        self.begin_string = begin_string
        self.begin_line_ending = begin_line_ending
        self.finished_message = finished_message
        self.finished_line_ending = finished_line_ending
        
        self.returns_string = returns_string
        if self.returns_string:
            self.returned_string = ''
        else:
            self.returned_string = None    
        self.enable_print = enable_print
        
    def __enter__(self):
        self.returned_string = WrappingPerformanceTimer.print_generic_progress_message(self.begin_string, self.begin_line_ending, self.returns_string, self.enable_print)
        # self.returned_string = WrappingMessagePrinter.print_file_progress_message(self.filepath, self.action, self.contents_description, self.print_line_ending, returns_string=self.returns_string)
        
    def __exit__(self, *args):
        self.exit_time = time.time()
        self.elapsed_time = (self.exit_time - self.start_time)
        if self.enable_print:
            # print(f'Elapsed Time = {self.elapsed_time}')
            print(f'{self.finished_message} Elapsed Time = {self.elapsed_time}', end=self.finished_line_ending)
        if self.returns_string:
            # self.returned_string = f'Elapsed Time = {self.elapsed_time}'
            self.returned_string = f'{self.returned_string}{self.finished_message} Elapsed Time = {self.elapsed_time}{self.finished_line_ending}'
        
        # if self.enable_print:
        #     print(self.finished_message, end=self.finished_line_ending)
        # if self.returns_string:
        #     self.returned_string = f'{self.returned_string}{self.finished_message}{self.finished_line_ending}'
         
    @classmethod
    def print_generic_progress_message(cls, begin_string, begin_line_ending, returns_string, enable_print):
        if returns_string:
            out_string = f'{begin_string}...'
            if enable_print:
                print(out_string, end=begin_line_ending)
            return f'{out_string}{begin_line_ending}'
        else:
            if enable_print:
                print(f'{begin_string}...', end=begin_line_ending)
            