/* cpcdos_helper.c
   Helper minimum pour exécuter commandes système depuis le engine.
   Compile: gcc cpcdos_helper.c -o cpcdos_helper
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: cpcdos_helper <commande>\n");
        return 1;
    }
    char *cmd = argv[1];
    if (strcmp(cmd,"shutdown")==0) {
        printf("Shutdown requested\n");
        // Use systemctl poweroff (requires sudo)
        system("systemctl poweroff");
        return 0;
    } else if (strcmp(cmd,"reboot")==0) {
        printf("Reboot requested\n");
        system("systemctl reboot");
        return 0;
    } else if (strncmp(cmd,"exec",4)==0) {
        // exec <command> -> run the rest
        char cmdline[1024] = {0};
        // combine argv[1..] into a command if needed
        if (argc >= 2) {
            // argv[1] starts with "exec", so allow trailing string in argv[1] or further args
            if (strlen(argv[1]) > 4) {
                snprintf(cmdline, sizeof(cmdline), "%s &", argv[1] + 5);
            } else {
                // join remaining args
                int i;
                for (i=2;i<argc && strlen(cmdline) < sizeof(cmdline)-100;i++) {
                    strncat(cmdline, argv[i], sizeof(cmdline)-strlen(cmdline)-1);
                    strncat(cmdline, " ", sizeof(cmdline)-strlen(cmdline)-1);
                }
                strncat(cmdline, "&", sizeof(cmdline)-strlen(cmdline)-1);
            }
            printf("Executing: %s\n", cmdline);
            system(cmdline);
            return 0;
        }
    } else {
        // fallback: run provided arg as system command
        char call[1024];
        snprintf(call, sizeof(call), "%s", cmd);
        printf("System call: %s\n", call);
        system(call);
        return 0;
    }
    return 1;
}
