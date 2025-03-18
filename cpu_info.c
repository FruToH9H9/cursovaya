#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <psapi.h>
#include <windows.h>

typedef struct {
    char name[256];
    float cpu_percent;
    float memory_usage;
} ProcessInfo;

__declspec(dllexport) int get_process_info(ProcessInfo* processes, int max_processes) {
    DWORD processes_list[1024], cbNeeded, numProcesses;
    unsigned int i;

    // Получаем список процессов
    if (!EnumProcesses(processes_list, sizeof(processes_list), &cbNeeded)) {
        return 0;
    }

    numProcesses = cbNeeded / sizeof(DWORD);
    int process_count = 0;

    for (i = 0; i < numProcesses && process_count < max_processes; i++) {
        DWORD processID = processes_list[i];
        if (processID == 0) continue;  // Пропустить процессы без ID

        // Открываем процесс для получения информации
        HANDLE hProcess = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, FALSE, processID);
        if (hProcess == NULL) continue;

        // Получаем имя процесса
        char processName[256] = "<неизвестно>";
        HMODULE hMod;
        DWORD cbNeeded;

        // Получаем имя модуля
        if (EnumProcessModules(hProcess, &hMod, sizeof(hMod), &cbNeeded)) {
            GetModuleBaseNameA(hProcess, hMod, processName, sizeof(processName) / sizeof(char));
        }

        // Получаем информацию о памяти
        PROCESS_MEMORY_COUNTERS pmc;
        if (GetProcessMemoryInfo(hProcess, &pmc, sizeof(pmc))) {
            processes[process_count].cpu_percent = 0.0f;  // Здесь можно добавить вычисление CPU
            processes[process_count].memory_usage = pmc.WorkingSetSize / 1024.0f / 1024.0f;  // В МБ
            strncpy(processes[process_count].name, processName, sizeof(processes[process_count].name));
        }

        // Увеличиваем количество процессов
        process_count++;

        // Закрываем дескриптор процесса
        CloseHandle(hProcess);
    }

    return process_count;
}

int main() {
    ProcessInfo processes[1024];
    int num_processes = get_process_info(processes, 1024);

    // Выводим информацию о процессах
    for (int i = 0; i < num_processes; i++) {
        printf("Process name: %s\n", processes[i].name);
        printf("Memory usage: %.2f MB\n", processes[i].memory_usage);
        // Здесь можно добавить вывод для CPU
    }

    return 0;
}
