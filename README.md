# INRain

A super simple beginner scripting language — a mix of batch and Python.
Runs `.inr` and `.inrain` files. Made to work off a USB drive.

## Requirements
- Python 3 installed on the Windows machine (get it from python.org, check
  "Add Python to PATH" during install)
- tkinter (comes bundled with Python automatically) — needed for GUI commands

## Setup (one time per computer)
1. Copy the whole `INRain` folder onto your USB drive.
2. Plug the USB in, open CMD, `cd` into the INRain folder:
   ```
   E:
   cd INRain
   ```
3. Run this once so `INRain` works from anywhere:
   ```
   setup_inrain.bat
   ```
   (Close and reopen CMD after this.)

## Running a script
```
INRain myscript.inr
```
or just double check you're in the folder and run:
```
INRain.bat myscript.inr
```

## The INRain Language

### Print text
```
print Hello World!
```

### Variables
```
set name = Bob
print Hello, {name}!
```
Use `{variable}` anywhere in text to insert a variable's value.

### Math
```
set x = 5
add x 3        REM x is now 8
sub x 1        REM x is now 7
mul x 2        REM x is now 14
div x 7        REM x is now 2
```

### Ask the user for input (text-based)
```
ask name What is your name?
print Nice to meet you, {name}!
```

### If / Else
```
if age >= 18:
    print You are an adult!
else:
    print You are a minor!
end
```
Works with `==`, `!=`, `>`, `<`, `>=`, `<=`

### Loops
```
loop 5:
    print Looping!
end
```
```
set count = 0
while count < 3:
    print count is {count}
    add count 1
end
```

### Wait / pause
```
wait 2      REM waits 2 seconds
```

### Run a real CMD command
```
run dir
run echo hello from cmd
```

### Clear the screen
```
clear
```

### Comments
```
REM this is ignored... actually use # instead:
# this is a comment
```

## GUI Commands (like tkinter, simplified)

### Open a window with text
```
gui Hello there!
```

### Add a button that runs a command when clicked
```
button Click Me -> print You clicked!
```

### Popup message box
```
popup This is a popup message!
```

### Popup text input box (GUI version of "ask")
```
input_box name What is your name?
print Hi {name}!
```

## Full Example
```
print Welcome to INRain!
ask name What is your name?
print Hello, {name}!

set age = 0
ask age How old are you?
if age >= 18:
    print You're an adult, {name}.
else:
    print You're still a minor, {name}.
end

gui Welcome, {name}!
button Say Hi -> popup Hi there!
button Close -> print Goodbye!
```

Save any of this as `myfile.inr` or `myfile.inrain` and run:
```
INRain myfile.inr
```
