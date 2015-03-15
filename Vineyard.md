# Introduction #

Vineyard is a cross platform render management tool for managing render farms. It consists of a worker service or daemon that digests jobs submitted to it from a render management application. Url encoded job submissions make additional submission sources easy, and integrated submission workflows can easily be integrated into the authoring tools. Engine plugins can be developed to handle additional job types. Current engines include After Effects CS4, 3Delight, and Maya.


## Application Overview ##

The main architecture consists of worker nodes that load render engines on the slave machines, broadcast special packets for auto-discovery by the clients (if configured), and listen for incoming render job assignments via http on a pre-configured port. Jobs are submitted via the url encoded format from a submission panel.

The client gui is written in PyQt. There is a worker node table, a job/task panel to display current and recently completed tasks, a log view, and a submission panel. The entire system is intended to be runtime configured, with a menu option to change port numbers and auto-discovery settings.

User, group, and privileges are planned, and I would like to implement it using domain authorization and privileges, which would make the system dependent on internal IT setups for different features. For example, a user would need to be a part of a certain group within the domain in order to kill a render job. I'm not sure if this is teh best idea for all studios though. I would like to get some feedback on this as well as any other features, including additional render engines, so please comment!