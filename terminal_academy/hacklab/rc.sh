# Shell hook for the player container (Part 2).
#
# This file is bind-mounted into the player container at /lab/rc.sh and loaded
# with `bash --rcfile /lab/rc.sh`. After every command, it appends one line
#     EPOCH<TAB>CWD<TAB>COMMAND
# to /lab/events/shell.log, which the host's diagram server reads live.
#
# WHY a hook and not a fake shell: the player uses a real bash. We only watch
# it from the side, the same way a real security team would watch a host.

# Make the history available so we can read the last command the player typed.
export HISTFILE=/lab/events/.bash_history
export HISTCONTROL=
shopt -s histappend 2>/dev/null

# Append one event line. We read the just-finished command from `history 1`
# and strip its leading number. PWD is the folder the player is in now.
__ta_log() {
    local last
    last=$(HISTTIMEFORMAT= history 1 2>/dev/null | sed 's/^ *[0-9][0-9]*  *//')
    # The very first prompt has no previous command; skip the empty case.
    if [ -n "$last" ]; then
        printf '%s\t%s\t%s\n' "$(date +%s)" "$PWD" "$last" >> /lab/events/shell.log 2>/dev/null
    fi
}

# Run the hook before each prompt, keeping any PROMPT_COMMAND already set.
case ";${PROMPT_COMMAND};" in
    *";__ta_log;"*) : ;;  # already installed
    *) PROMPT_COMMAND="__ta_log${PROMPT_COMMAND:+;$PROMPT_COMMAND}" ;;
esac

# A clear, friendly prompt so the player always sees where they are.
PS1='\[\e[1;36m\]player@\h\[\e[0m\]:\[\e[1;33m\]\w\[\e[0m\]$ '

echo "You are inside the lab. Type 'exit' to leave. The diagram updates as you work."
