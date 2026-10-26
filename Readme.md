### **1.IMPORT LIBRARIES**



*import tkinter as tk*

*from tkinter import ttk, messagebox*

*from datetime import datetime,date*

*import oracledb*

*import uuid*



**tkinter** - Creates application's GUI/Window

**ttk** - Dropdown ,buttons and tables

**messagebox** - Warming, error and success popups

**datetime** - Handles date and time

**oracle db** - Python connects to oracle

**uuid** - Generates unique ticket IDs



### **2.ORACLE DATABASE CONNECTION**



*DB\_USER = "BUSGO"*

*DB\_PASSWORD = "Busgo123"*

*DB\_DSN = "localhost:1521/XEPDB1"*



**BUSGO** - Username

**Busgo123** - password

**localhost:1521/XEPDB1** - Database Server , port And Service name.



### **3.MAIN APPLICATION CLASS**



*class BusGoApp:*

&#x20;   *def \_\_init\_\_(self, root):*



**class BusgoApp** - Blueprint of application

**\_\_init\_\_()** - Automatically runs when application object is created.



*self.root = root*

*self.root.title("MI BUS- Bus Booking System")*

*self.root.geomtry("1050x700")*

*self.root.configure(bg="#f0f4f8")*



**self.root** - Stores window in self.root

**title()** - Set title of window

**Geometry()** - Set Height and width of window

**configure()** - Set Background Colour



*self.selected\_bus = None*

*self.selected\_seats = set()*

*self.bus\_rows = \[]*

*self.ticket\_id = None*



**Selected\_bus** - bus selected by usersera

**Selcted\_Seats** - seat selected by user

**bus\_rows** - bus information by search

**ticket\_id** - identifier of booked ticket



### **4.CREATING APPLICATION PAGES**



*self.pages = {}*

*for name in (*

&#x20; *"Home", "Search", "Seats", "Passenger",*

&#x20; *"Payment", "Ticket", "Bookings", "Cancellation"*

*):*

&#x20; *self.pages\[name] = tk.Frame(self.container, bg="#f0f4f8")*





### **5.HOW DOES PAGE CHANGE**



*def show\_page(self, name):*

&#x20;*for page in self.pages.values():*

&#x20;  *page.pack\_forget()*

&#x20;*self.pages\[name].pack(fill="both", expand=True)*



**self.pages.values()** - access all pages

**pack\_forgot()** - Hide current displayed page

**pack()** - It Shows Requested page



### 

### **6.SEARCH BUSES PAGE**



*self.pickup = tk.StringVar()*

*self.destination = tk.StringVar()*

*self.journey\_date = tk.StringVar(value=date.today().isoformat())*



**stringVar()** - Stores tkinter input value



*self.bus\_tree = ttk.Treeview(p, columns=columns, show="headings", height=11)*



**Treeview** -  Search result show in table. ex, Bus Id, Operator, route,departure.



*cur.execute("SELECT DISTINCT pickup FROM bg\_buses"*

&#x09;    *"WHERE active ='Y' ORDER BY pickup")*



**SELECT DISTINCT pickup** - remove duplicate pickup locations

**FROM bg\_buses** - pick data from bus table

**WHERE active='Y'**- Take only active buses locations

**ORDER BY pickup** - location in alphabetical order



*pickups = \[r\[0] for r in cur.fetchall()]*



**fetchall()** - saari query results lata hai

**r\[0]** - har row ka pehla column nikalti hai

### 

### **7.PASSENGER DETAILS**



*def continue\_passenger(self)*

&#x20;*if not self.selected\_seats:*



**Agar koi seat select nahi ki to warning deta hai**





### **8.CONFIRM BOOKING**



*total = len(self.selected\_seats)\*float(bus\[7])*

*ticket = "BG"+uuid.uuid4().hex\[:10].upper()*



**total** - calculate amount of selected seats

**uuid.uuid4()**- generates unique Identifires

**.hex\[:10]** - pahile 10 hexa decimal leta hai

**upper**- char ko uppercase karta hai

**BG** - Ticket id me prefix add karta hai









