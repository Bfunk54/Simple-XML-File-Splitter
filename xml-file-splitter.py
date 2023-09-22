import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QTextEdit, QFileDialog, QVBoxLayout, QWidget


class XMLFileSplitter(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('XML File Splitter')
        self.setGeometry(100, 100, 600, 400)

        # Widgets
        self.srcLabel = QLabel('Source:')
        self.outDirLabel = QLabel('Output Dir:')
        self.maxSizeLabel = QLabel('Max File Size (MB):')  # Added a label for max file size
        self.srcFileDisplay = QLineEdit()
        self.outDirDisplay = QLineEdit()
        self.maxSizeDisplay = QLineEdit()  # Added an input field for max file size
        self.browseSrcFile = QPushButton('Browse File')
        self.browseOutDir = QPushButton('Browse Dir.')
        self.statusDisplay = QTextEdit()
        self.startButton = QPushButton('Start')
        self.exitButton = QPushButton('Exit')

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.srcLabel)
        layout.addWidget(self.srcFileDisplay)
        layout.addWidget(self.browseSrcFile)
        layout.addWidget(self.outDirLabel)
        layout.addWidget(self.outDirDisplay)
        layout.addWidget(self.browseOutDir)
        layout.addWidget(self.maxSizeLabel)
        layout.addWidget(self.maxSizeDisplay)
        layout.addWidget(self.statusDisplay)
        layout.addWidget(self.startButton)
        layout.addWidget(self.exitButton)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Button Click Events
        self.browseSrcFile.clicked.connect(self.getFileName)
        self.browseOutDir.clicked.connect(self.getOutDir)
        self.startButton.clicked.connect(self.startProc)
        self.exitButton.clicked.connect(self.sysExit)

        self.procInfo = {}

    def getFileName(self):
        fileName, _ = QFileDialog.getOpenFileName()
        self.srcFileDisplay.setText(fileName)
        self.procInfo['filename'] = fileName

    def getOutDir(self):
        outputDir = QFileDialog.getExistingDirectory()
        self.outDirDisplay.setText(outputDir)
        self.procInfo['outputdir'] = outputDir

    def get_max_file_size(self):
        while True:
            try:
                size_mb = float(self.maxSizeDisplay.text())
                if size_mb <= 0:
                    self.statusDisplay.append("Please enter a positive value for max file size.")
                else:
                    return size_mb
            except ValueError:
                self.statusDisplay.append("Invalid input. Please enter a valid number for max file size.")

    def writeHeader(self, currentFile):
        header = '''
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
    xmlns:excerpt="http://wordpress.org/export/1.2/excerpt/"
    xmlns:content="http://purl.org/rss/1.0/modules/content/"
    xmlns:wfw="http://wellformedweb.org/CommentAPI/"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:wp="http://wordpress.org/export/1.2/"
>
<channel>
<wp:wxr_version>1.2</wp:wxr_version>'''

        currentFile.write(header)

    def writeFooter(self, currentFile):
        footer = '''
</channel>
</rss>'''

        currentFile.write(footer)

    def sysExit(self):
        sys.exit(1)

    def startProc(self):
        if 'filename' in self.procInfo and 'outputdir' in self.procInfo:
            filePath, fileName = os.path.split(self.procInfo['filename'])
            fileNameTxt, fileNameExt = os.path.splitext(fileName)
            outDir = self.procInfo['outputdir']
            max_file_size_mb = self.get_max_file_size()  # Get max file size from user input

            self.statusDisplay.append('Reading file ' + fileName)
            xmlFileObj = open(os.path.join(filePath, fileName), "r")
            xmlFile = xmlFileObj.read()
            totalCount = len(xmlFile)
            iteration = 0
            currentCount = 0
            maxInc = int(max_file_size_mb * 1024 * 1024)  # Convert MB to bytes
            EOF = False
        else:
            if 'filename' not in self.procInfo:
                self.statusDisplay.append('Source file not selected')
            if 'outputdir' not in self.procInfo:
                self.statusDisplay.append('Output Directory not selected')
            self.statusDisplay.append('ERROR: Source file or Output Directory not selected')
            self.statusDisplay.append('Exiting...')
            return

        while not EOF:
            currentFileName = f"{fileNameTxt}_{iteration}{fileNameExt}"
            currentFile = open(os.path.join(outDir, currentFileName), 'w')
            self.statusDisplay.append('Writing file ' + currentFileName)

            if iteration != 0:
                self.writeHeader(currentFile)

            if (currentCount + maxInc) < totalCount:
                xFile_i = xmlFile[currentCount:currentCount + maxInc]
                incrFile = xFile_i.rfind('</item>') + len('</item>')
                currentFile.write(xFile_i[:incrFile])
                currentCount += incrFile
            else:
                xFile_i = xmlFile[currentCount:]
                currentFile.write(xFile_i)
                self.statusDisplay.append('Finished processing')
                EOF = True

            if not EOF:
                self.writeFooter(currentFile)

            iteration += 1


def main():
    app = QApplication(sys.argv)
    window = XMLFileSplitter()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
