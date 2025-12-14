# Hterm
## 实现思路
``` shell
+-----------------------------------------------------------------+
|                Session (Coordinator)                            |
|  * Role: Lifecycle Mgmt, Signal/Slot Binding, , Data Forwarding |
+------------------------------+----------------------------------+
               |                           |
               | (Composition)             | (Composition)
               v                           v
+-------------------------------+    +-----------------------------+
|       Terminal (View/UI)      |    |   PtyChannel (Comm Model)   |
| * QAbstractScrollArea         |    | * ABC                       |
| * Role: Capture Input, Render |    | * Role: I/O & Protocol      |
+-------------+-----------------+    +-------------+---------------+
              |                                    |
              | (Signal: input)                    | (Signal: recv)
              |                                    |
              v                                    v
        +-------------------------------------------------+
        |                                                 |
        |                 Data Flow Process               |
        |                                                 |
        +-------------------------------------------------+
          
        (1) [User Input] -------------------->  Terminal 
        
        (2) Terminal     ---[signal_input]--->  Session 
        
        (3) Session      ---[send_data]------>  PtyChannel
        
        (4) PtyChannel   ----[send]---------->  Remote Shell
        
        (5) PtyChannel   <---[recv]-----------  Remote Shell
        
        (6) PtyChannel   ----[signal_recv]--->  Session
        
        (7) Session      ----[feed]---------->  Terminal
        
        (8) Terminal     -------------------->  [Render Screen]
```