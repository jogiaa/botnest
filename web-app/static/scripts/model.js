const documenters = {
    FILE: Symbol("file_documenter"),
    FOLDER: Symbol("folder_documenter"),
    SUMMARY: Symbol("summarizer"),
    SUMMARY_AUGMENTED: Symbol("summary_augmented"),
};

// create Model namespace
export const Model = {
    $: {
        availableModels: [
            {
                provider: "Meta",
                id: "llama3.2:1b",
                displayName: "Meta 3.2 [1 Billion] ",
            },
            {
                provider: "Meta",
                id: "llama3.2:3b",
                displayName: "Meta 3.2 [3 Billion] ",
            },
            {
                provider: "Google",
                id: "gemma3:1b",
                displayName: "Google Gemma 3 [1 Billion]",
            },
            {
                provider: "Deepseek",
                id: "deepseek-r1:8b",
                displayName: "Deepseek R1 [8 Billion]",
            },
            {
                provider: "Google",
                id: "codegemma:7b",
                displayName: "Google CodeGemma [7 Billion]",
            },
            {
                provider: "Meta",
                id: "codellama:7b",
                displayName: "Meta Code Llama [7 Billion]",
            },
            {
                provider: "Open AI",
                id: "gpt-oss:20b",
                displayName: "GPT OSS 20B",
            },
        ],
        documenterModes: [
            {
                id: documenters.FILE.description,
                displayName: "File Documenter",
            },
            {
                id: documenters.FOLDER.description,
                displayName: "Folder Documenter",
            },
            {
                id: documenters.SUMMARY.description,
                displayName: "Summarize File/Folder [Does not document]",
            },
            {
                id: documenters.SUMMARY_AUGMENTED.description,
                displayName: "Summary Augmented File/Folder Documenter",
            },
        ],
        modeConfig: {
            [documenters.FILE.description]: {
                sourceLabel: "3. Source File",
                sourceHelpText: "Enter the path to the file you want to document.",
                sourcePlaceholder: "/path/to/your/file.py",
                destinationLabel: "4. Destination File",
            },
            [documenters.FOLDER.description]: {
                sourceLabel: "3. Source Folder",
                sourceHelpText: "Enter the path of the folder you want to document.",
                sourcePlaceholder: "/path/to/your/folder",
                destEnabled: true,
                destinationLabel: "4. Destination Folder",
            },
            [documenters.SUMMARY.description]: {
                sourceLabel: "3. Source Folder/File",
                sourceHelpText: "Enter the path to the item you want to summarize.",
                sourcePlaceholder: "/path/to/your/item",
                destinationLabel: "4. Destination",
            },
            [documenters.SUMMARY_AUGMENTED.description]: {
                sourceLabel: "3. Source Folder/File",
                sourceHelpText:
                    "Enter the path to the item for summarization and documentation.",
                sourcePlaceholder: "/path/to/your/item",
                destinationLabel: "4. Destination Folder/File",
            },
        },
    },
};
