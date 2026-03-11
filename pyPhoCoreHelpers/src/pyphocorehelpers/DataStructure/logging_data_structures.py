from typing import Dict, List, Tuple, Optional, Callable, Union, Any
from typing_extensions import TypeAlias
from nptyping import NDArray
from copy import deepcopy
from attrs import define, field, Factory
import neuropy.utils.type_aliases as types
from pyphocorehelpers.programming_helpers import metadata_attributes
from pyphocorehelpers.function_helpers import function_attributes

# from pyphoplacecellanalysis.External.pyqtgraph.Qt import QtCore, QtGui, QtWidgets
# from qtpy import QtCore, QtWidgets
from PyQt5 import QtCore, QtWidgets, QtGui


@define(repr=False, slots=False)
class LoggingBaseClass(QtCore.QObject):
    """ 
    
    Used By: Spike3DRasterBottomPlaybackControlBar, 
    
    from pyphocorehelpers.DataStructure.logging_data_structures import LoggingBaseClass, LoggingBaseClassLoggerOwningMixin
    
    logger = LoggingBaseClass(log_records=[])
    logger.sigLogUpdated.connect(self.on_log_updated)
    
    
    """
    log_records: List[str] = field(default=Factory(list))
    debug_print: bool = field(default=False)

    sigLogUpdated = QtCore.pyqtSignal(object) # passes self
    sigLogUpdateFinished = QtCore.pyqtSignal() # passes self

    @property
    def flattened_log_text(self) -> str:
        """The flattened_log_text property."""
        return self.get_flattened_log_text(flattening_delimiter='\n')
                                     

    def get_flattened_log_text(self, flattening_delimiter: str='\n', limit_to_n_most_recent: Optional[int]=None) -> str:
        """The flattened_log_text property."""
        if (limit_to_n_most_recent is not None) and (len(self.log_records) > limit_to_n_most_recent):
            active_log_records = self.log_records[-limit_to_n_most_recent:]
        else:
            active_log_records = self.log_records
        return flattening_delimiter.join(active_log_records)
        
    
    def __attrs_pre_init__(self):
        # super().__init__(parent=None) # normally have to do: super(ToggleButtonModel, self).__init__(parent)
        QtCore.QObject.__init__(self) # some inheritors of QObject seem to do this instead
        # note that the use of super() is often avoided because Qt does not allow to inherit from multiple QObject subclasses.


    def add_log_line(self, new_line: str, allow_split_newlines: bool = True, defer_log_changed_event:bool=False):
        """ adds an additional entry to the log """
        initial_log_text: str = deepcopy(self.flattened_log_text)
        
        ## start by splitting on any newlines
        if allow_split_newlines:
            new_lines = new_line.splitlines()
            self.log_records.extend(new_lines)
        else:
            self.log_records.append(new_line)
        
        post_log_text: str = deepcopy(self.flattened_log_text)
        did_log_change: bool = (initial_log_text != post_log_text)
        
        if did_log_change:
            if self.debug_print:
                print(f'log did change!!')
            self.sigLogUpdated.emit(self)
        else:
            if self.debug_print:
                print(f'log did not change!!')
            
        if not defer_log_changed_event:
            if self.debug_print:
                print(f'log did finish editing!!')
            self.sigLogUpdateFinished.emit()
            
    def add_log_lines(self, new_lines: List[str], allow_split_newlines: bool = True, defer_log_changed_event:bool=False):
        """ adds an additional entries to the log """
        initial_log_text: str = deepcopy(self.flattened_log_text)
    
        for a_line in new_lines:
            self.add_log_line(new_line=a_line, allow_split_newlines=allow_split_newlines, defer_log_changed_event=True)

        post_log_text: str = deepcopy(self.flattened_log_text)
        did_log_change: bool = (initial_log_text != post_log_text)

        if (not defer_log_changed_event):
            if self.debug_print:
                print(f'log did finish editing!!')
            self.sigLogUpdateFinished.emit()



@metadata_attributes(short_name=None, tags=['logging'], input_requires=[], output_provides=[], uses=[], used_by=['SpikeRasterBottomFrameControlsMixin', 'SpikeRasterBase'], creation_date='2025-01-06 16:01', related_items=[])
class LoggingBaseClassLoggerOwningMixin:
    """ Usage

    from pyphocorehelpers.DataStructure.logging_data_structures import LoggingBaseClass, LoggingBaseClassLoggerOwningMixin

    """
    @property
    def LoggingBaseClassLoggerOwningMixin_logger(self) -> Optional[LoggingBaseClass]:
        """`LoggingBaseClassLoggerOwningMixin`-conformance required property."""
        return self._logger
    
    @property
    def debug_print(self) -> bool:
        """`LoggingBaseClassLoggerOwningMixin`-conformance required property."""
        return self.params.get('debug_print', False)    
    @debug_print.setter
    def debug_print(self, value: bool):
        self.params.debug_print = value
    
    # @logger.setter
    # def logger(self, value: LoggingBaseClass):
    #     self._logger = value
        
    # @property
    # def attached_log_window(self) -> Optional[LoggingOutputWidget]:
    #     """The attached_log_window property."""
    #     return self._attached_log_window


    # @pyqtExceptionPrintingSlot(object)
    def on_log_updated(self, logger):
        if self.debug_print:
            print(f'LoggingBaseClassLoggerOwningMixin.on_log_updated(logger: {logger})')
        # logger: LoggingBaseClass
        target_text: str = self.LoggingBaseClassLoggerOwningMixin_logger.get_flattened_log_text(flattening_delimiter='|', limit_to_n_most_recent=3)
        # self.ui.txtLogLine.setText(target_text)
        ## don't need to update the connected window, as it will update itself
        

    # @pyqtExceptionPrintingSlot()
    def on_log_update_finished(self):
        if self.debug_print:
            print(f'LoggingBaseClassLoggerOwningMixin.on_log_update_finished()')
        # logger: LoggingBaseClass
        target_text: str = self.LoggingBaseClassLoggerOwningMixin_logger.get_flattened_log_text(flattening_delimiter='|', limit_to_n_most_recent=3)
        # self.ui.txtLogLine.setText(target_text)
        ## don't need to update the connected window, as it will update itself
        

    @function_attributes(short_name=None, tags=['logging', 'LoggingBaseClassLoggerOwningMixin'], input_requires=[], output_provides=[], uses=[], used_by=['add_log_lines'], creation_date='2025-01-06 11:26', related_items=[])
    def add_log_line(self, new_line: str, allow_split_newlines: bool = True, defer_log_changed_event:bool=False):
        """ adds an additional entry to the log """
        if self.debug_print:
            print(f'.add_log_line(...): self.LoggingBaseClassLoggerOwningMixin_logger: {self.LoggingBaseClassLoggerOwningMixin_logger.get_flattened_log_text()}')
        self.LoggingBaseClassLoggerOwningMixin_logger.add_log_line(new_line=new_line, allow_split_newlines=allow_split_newlines, defer_log_changed_event=defer_log_changed_event)
            
    @function_attributes(short_name=None, tags=['logging', 'LoggingBaseClassLoggerOwningMixin'], input_requires=[], output_provides=[], uses=['add_log_line'], used_by=['log_print'], creation_date='2025-01-06 11:26', related_items=[])
    def add_log_lines(self, new_lines: List[str], allow_split_newlines: bool = True, defer_log_changed_event:bool=False):
        """ adds an additional entries to the log """
        if self.debug_print:
            print(f'.add_log_lines(...): self.LoggingBaseClassLoggerOwningMixin_logger: {self.LoggingBaseClassLoggerOwningMixin_logger.get_flattened_log_text()}')
        self.LoggingBaseClassLoggerOwningMixin_logger.add_log_lines(new_lines=new_lines, allow_split_newlines=allow_split_newlines, defer_log_changed_event=defer_log_changed_event)
                    
    @function_attributes(short_name=None, tags=['logging', 'print', 'LoggingBaseClassLoggerOwningMixin'], input_requires=[], output_provides=[], uses=[], used_by=[], creation_date='2025-01-06 11:25', related_items=[])
    def log_print(self, *args):
        """ adds an additional entry to the log """
        print(*args)
        self.add_log_lines(new_lines=args, defer_log_changed_event=False)


class LoggingConsoleWidget(QtWidgets.QWidget):
    """A simple ready-to-use pyqt5-based logging console widget that I can log my application out to as it runs, preferably asynchronously
    
    
    """
    def __init__(self, logger: Optional[LoggingBaseClass]=None, parent=None):
        super().__init__(parent=parent)
        self.logger = logger or LoggingBaseClass(log_records=[])
        self.initUI()
        self.logger.sigLogUpdated.connect(self.on_log_updated)
        self.logger.sigLogUpdateFinished.connect(self.on_log_update_finished)

    def initUI(self):
        self.layout = QtWidgets.QVBoxLayout(self)
        self.textEdit = QtWidgets.QTextEdit()
        self.textEdit.setReadOnly(True)
        self.layout.addWidget(self.textEdit)
        self.setLayout(self.layout)

    @QtCore.pyqtSlot(object)
    def on_log_updated(self, logger):
        # print(f'LoggingConsoleWidget.on_log_updated(logger: {logger})')
        # logger: LoggingBaseClass
        # target_text: str = self.logger.get_flattened_log_text(flattening_delimiter='\n', limit_to_n_most_recent=None)
        # self.textEdit.setText(target_text)
        # self.textEdit.repaint()
        pass

    @QtCore.pyqtSlot()
    def on_log_update_finished(self):
        # print(f'LoggingConsoleWidget.on_log_update_finished()')
        target_text: str = self.logger.get_flattened_log_text(flattening_delimiter='\n', limit_to_n_most_recent=None)
        self.textEdit.setText(target_text)
        self.textEdit.repaint()
        
    def add_log_line(self, new_line: str, allow_split_newlines: bool = True, defer_log_changed_event:bool=False):
        """ adds an additional entry to the log """
        self.logger.add_log_line(new_line=new_line, allow_split_newlines=allow_split_newlines, defer_log_changed_event=defer_log_changed_event)
            
    def add_log_lines(self, new_lines: List[str], allow_split_newlines: bool = True, defer_log_changed_event:bool=False):
        """ adds an additional entries to the log """
        self.logger.add_log_lines(new_lines=new_lines, allow_split_newlines=allow_split_newlines, defer_log_changed_event=defer_log_changed_event)

