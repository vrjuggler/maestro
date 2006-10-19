#
# FileAssociation - Associates a file extension with a program.
#
# Example:
#  Push ".ensem"                               - Extension
#  Push "MaestroEnsemble"                      - Name
#  Push "Ensemble File"                        - Label
#  Push "$OUTDIR\ensemble.ico"                 - Icon
#  Push "Load Ensemble into Maestro GUI"       - Context Menu Text
#  Push '"$OUTDIR\Maestro.py" "%1"'            - Maestro GUI Program
#  Call FileAssociation
#

Var EXT
Var NAME
Var DESC
Var ICON
Var MAESTRO_TOOL_TIP
Var MAESTRO_COMMAND

Function FileAssociation
  Pop $MAESTRO_COMMAND
  Pop $MAESTRO_TOOL_TIP
  Pop $ICON
  Pop $DESC
  Pop $NAME
  Pop $EXT

#"TestExtExists:"
  ReadRegStr $1 HKCR $EXT ""
  # If empty goto no backup
  StrCmp $1 "" "WriteExt" "AddActions"
  # If existing type is the same as ours write ext
  StrCmp $1 $NAME "WriteExt" "AddActions"
  # Write old value to backup NOTE: We do not want to overwrite old value
  #WriteRegStr HKCR $EXT "backup_val" $1
"WriteExt:"
  WriteRegStr HKCR $EXT "" $NAME
  # Test Name Exists
  ReadRegStr $0 HKCR $NAME ""
  StrCmp $0 "" "WriteName" "AddActions"
"WriteName:"
  WriteRegStr HKCR $NAME "" $DESC

"AddActions:"
  # Regardless of the $NAME we want to use the value associated with
  # the file extension.
  ReadRegStr $1 HKCR $EXT ""
  WriteRegStr HKCR "$1\shell" "" "open"
  # If we have the associations add icon
  StrCmp $1 $NAME 0 +2
  WriteRegStr HKCR "$1\DefaultIcon" "" $ICON
  WriteRegStr HKCR "$1\shell\$NAME" "" $MAESTRO_TOOL_TIP
  WriteRegStr HKCR "$1\shell\$NAME\command" "" $MAESTRO_COMMAND

FunctionEnd

#
# RemoveFileAssociation - Associates a file extension with a program.
#
# Example:
#  Push ".ensem"                               - Extension
#  Push "MaestroEnsemble"                      - Name
#
Function un.RemoveFileAssociation
  Pop $NAME
  Pop $EXT

  ReadRegStr $1 HKCR $EXT ""
  StrCmp $1 $NAME "RemoveAll" "RemoveActions"
"RemoveAll:"
  DeleteRegKey HKCR $EXT
  DeleteRegKey HKCR $NAME
  Goto "DoneRFA"
"RemoveActions:"
  # If we have the associations add icon
  ReadRegStr $1 HKCR $EXT ""
  DeleteRegKey HKCR "$1\shell\$NAME"
"DoneRFA:"

FunctionEnd
