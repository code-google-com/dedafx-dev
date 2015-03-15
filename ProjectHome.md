Vineyard is growing a bit dated as I have not worked on it since starting as a Technical Artist at CCP Games. I've grown better at python since working with a predominantly Python studio. My latest code sample can be found under the python/gui/qt/nodeview folder in the source. Go to source->browse to check it out without having to download everything locally.

# Vineyard #

Vineyard is a distributed render management system written in Python. It is cross platform currently working on both Windows and Linux (I don't own a Mac, or a turtleneck. Maybe some of you can help me with the mac development).<br>
Vineyard consists of two main parts, a server that processes render jobs submitted to it, and a client interface for farm and job queue management and job submission. The server side runs as either a Windows service or a Linux daemon process on any machine to be used for rendering. These worker nodes have an autodiscovery feature, broadcasting a magic packet on a subnet that the clients read. Upon discovery, the node is entered into a local SQLite database on the client machine.<br>
The server also runs a http server in a thread. This is its main interface for status information and job submission. Status info is delivered in a JSON format to the requesting client from this http server thread. The client has a thread to periodically poll the worker nodes that the client knows about (the ones stored in its local database). <br>
Both the client and the worker nodes have a plug-in system for the render engines. These engines are what do the actual render processing, launching and watching the render process in a job-queue thread on the server. <br>
While this system is still in development, it is rapidly approaching it's first release candidate. I am always open to suggestions, critique and comments, which can be submitted on the dedafx-dev website.<br>
While an official release candidate is on the horizon, bleeding edge code can be retrieved via svn. <br>
I am currently using sphinx for documentation (mostly todo before the first release), built using py2exe and put into an installer for easy use for Windows users. Linux users will still need to use <code>python setup.py install</code> to install the Vineyard package. More details will be available on the dedafx-dev website as I make them available. <br>
Enjoy!<br>
<br>
<br>
<h1>Alienbrain Python Interface</h1>

The alienbrain.py file is a python interface to Alienbrain Revision Control. While I do not recommend Alienbrain (svn is by far more reliable), it is used by some artists. I wrote this module to interact with the Alienbrain server through various Python tools. I architected a system to interact with two forms of revision control, Alienbrain (art team) and Starteam (programmers) to retrieve game assets and auto-package them into installers. This is used to significantly cut down the overhead involved with all of the manual labor associated with creating a data installer. It fixed the issue of incorrect files being included, and dramatically reducing costs in both production and QA.