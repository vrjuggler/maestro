# Maestro is Copyright (C) 2006 by Infiscape
#
# Original Author: Aron Bierbaum
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

from PyQt4 import QtCore, QtGui

class LogWidget(QtGui.QWidget):
   """
   A class for displaying logging messages.

   LogWidget is a simple class to be plugged in a LogView. 
   It displays lines of text without interpretation of richtext or html tags. 
   Neither are special characters like newlines or tabs interpreted.
   The widget can either store all the strings sent to it (the default) or 
   can limit the number of lines to store. In this case the oldest lines 
   are discarded when new lines arrive.
   """
   def __init__(self, parent=None, name=None):
      """
      Constructor
      
      @param parent parent widget (QtGui.QWidget)
      @param name name of this widget (string or QString)
      """
      QtGui.QWidget.__init__(self, parent)
      self.__listLines = QtCore.QStringList()
      self.__maxLines = 400
      self.__maxLen = 0
      self.__attachToBottom = True
      # Use a fixed width font.
      self.setFont(QtGui.QFont('Courier'))

   def attachToBottom(self):
      return self.__attachToBottom

   def setAttachToBottom(self, val):
      self.__attachToBottom = val

   def preferredBackgroundColor(self):
      """
      Reimplemented to return colorgroup().base().
      
      @return preferred background colour (QColor)
      """
      return self.palette().base().color()
      
   def paintEvent(self, evt):
      """
      Reimplemented for custom painting.
      
      @param evt the paint event object (QPaintEvent)
      """
      fm = self.fontMetrics()
      height = fm.height()
      x = 2
      y = height
      p = QtGui.QPainter(self)

      for line in self.__listLines:
         p.drawText(x, y, line)
         y += height
         
   def handleSetMaxLines(self, val):
      """
      Sets the maximum number of lines to be shown. 
      
      @param val maximum number of lines to be displayed
            If val is <= 0 then there will be no limit. If the maximum number 
            of lines is appended, the oldest are discarded.
      """
      self.__maxLines = val
      
   def append(self, text):
      """
      Public method to append text to the messages. 
      
      When the LogWidget is already scrolled to the bottom, it will 
      further scroll down to display the newly added line. If the 
      scrolling position is not at the end, this position is not changed.
      
      @param text text to be appended (string or QString)
      """
      try:
         lines = text.split('\n')
         num_new_lines = len(lines)
         num_lines = self.__listLines.count()

         # Try to speed up the append process by removing as many lines
         # from the buffer right now.
         if (num_lines + num_new_lines > self.__maxLines):
            num_extra_lines = (num_lines + num_new_lines) - self.__maxLines
            self.__listLines = self.__listLines[num_extra_lines:]
            

         fm = self.fontMetrics()
         for line in lines:
            self.__listLines.append(line)
            self.__maxLen = max(self.__maxLen, fm.boundingRect(line).width()+2)
            if self.__maxLines > 0 and self.__listLines.count() > self.__maxLines:
               self.__listLines = self.__listLines[-(self.__maxLines):]
            self.setMinimumSize(self.__maxLen, self.__listLines.count()*fm.height() + 2)


         self.emit(QtCore.SIGNAL('sizeChanged'), (self,))
         self.update()
         #QtGui.qApp.processEvents(QtCore.QEventLoop.AllEvents, 10)
      except Exception, ex:
         print "EXCEPTION: ", ex
      
   def clear(self):
      """
      Public method to delete all strings from the internal buffer and clears the display.
      """
      self.__listLines.clear()
      fm = self.fontMetrics()
      self.setMinimumSize(QtCore.QSize(min(200, self.__maxLen*fm.maxWidth()),
                        min(200, self.__listLines.count()*fm.height() + 2)))
      self.resize(1, 1)
      self.emit(QtCore.SIGNAL('sizeChanged'), (self,))
      self.update()
      
   def copy(self):
      """
      Public method to copy all strings from the internal buffer to the clipboard.
      """
      QtGui.qApp.clipboard().setText(self.__listLines.join("\n"), QtGui.QClipboard.Clipboard)

