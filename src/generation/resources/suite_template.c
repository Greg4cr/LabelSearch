#include <stdio.h>
#include "tcas_labels_instrumented.c"

// Array indexing test entries.
// tests[0] indicates number of tests
// tests[1] corresponds to test001(), etc.
int tests[3]={2,1,1};

// Flag for printing obligation scores to a CSV file at the end of execution.
int print = 1;
char* fileName = "test.csv";

// Flag for printing obligation scores to the screen at the end of execution.
int screen = 1;

// Prints obligation scores to the screen
void printScoresToScreen(){
    printf("# Obligation, Score (Unnormalized)\n");
    int obligation;
    for(obligation=1; obligation<=obligations[0]; obligation++){
        printf("%d, %f\n",obligation,obligations[obligation]);
    }
}

// Prints obligation scores to a file
void printScoresToFile(){
    FILE *outFile = fopen(fileName,"w");
    fprintf(outFile, "# Obligation, Score (Unnormalized)\n");
    int obligation;
    for(obligation=1; obligation<=obligations[0]; obligation++){
        fprintf(outFile,"%d, %f\n",obligation,obligations[obligation]);
    }
    fclose(outFile);
}

// Test Cases
void test001(){
    ALIM();
    Inhibit_Biased_Climb();
    Inhibit_Biased_Climb();    
}

void test002(){
    initialize();
    Non_Crossing_Biased_Climb();
    Non_Crossing_Biased_Descend();
}

// Top-level test runner.
void runner(){
    if(tests[1] == 1)
        test001();
    if(tests[2] == 1)
        test002();

    if(screen == 1)
        printScoresToScreen();
    if(print == 1)
        printScoresToFile();
}

int main(){
    runner();
    return(0);
}
