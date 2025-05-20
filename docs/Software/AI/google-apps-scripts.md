We used this code:

```
// === CONFIGURATION ===
// The exact phrase to search for within the content of your Google Drive files.
const SEARCH_QUERY = 'fullText contains "Knowledge Aura"';

// The name of the folder where matching files will be copied.
// If this folder doesn't exist in the root of your Drive, it will be created.
const TARGET_FOLDER_NAME = "Classification";
// === END CONFIGURATION ===

/**
 * Main function to be executed.
 * This function finds documents containing the SEARCH_QUERY and copies them
 * to the TARGET_FOLDER_NAME.
 */
function copyFilesWithKeyword() {
  try {
    // 1. Get or create the target folder
    const targetFolder = getOrCreateFolder_(TARGET_FOLDER_NAME);
    if (!targetFolder) {
      const errorMessage = `Failed to get or create the target folder: "${TARGET_FOLDER_NAME}". Script cannot continue. Check logs for details.`;
      Logger.log(errorMessage);
      Browser.msgBox("Error", errorMessage, Browser.Buttons.OK);
      return;
    }
    Logger.log(`Using target folder: "${TARGET_FOLDER_NAME}" (ID: ${targetFolder.getId()})`);

    // 2. Search for files containing the keyword
    Logger.log(`Searching for files with query: ${SEARCH_QUERY}`);
    const files = DriveApp.searchFiles(SEARCH_QUERY);

    let filesFoundCount = 0;
    let filesCopiedCount = 0;
    let filesSkippedCount = 0; // Count files that are already the script's own output (e.g. the script file itself if named with keyword)

    if (!files.hasNext()) {
      Logger.log(`No files found matching the query: "${SEARCH_QUERY}".`);
      Browser.msgBox("Information", `No files found containing the phrase "${SEARCH_QUERY}".`, Browser.Buttons.OK);
      return;
    }

    // 3. Iterate through found files and copy them
    while (files.hasNext()) {
      const file = files.next();
      filesFoundCount++;
      Logger.log(`Processing file ${filesFoundCount}: "${file.getName()}" (ID: ${file.getId()}, Owner: ${file.getOwner() ? file.getOwner().getEmail() : 'N/A'})`);

      // Avoid copying the script file itself if it happens to contain the keyword and is in the search results.
      // Also avoid copying files that are already in the target folder (simplistic check, assumes it's not the source)
      if (ScriptApp.getScriptId() === file.getId()) {
          Logger.log(`Skipping copy of the script file itself: "${file.getName()}"`);
          filesSkippedCount++;
          continue;
      }
      
      // Check if the file's parent is already the target folder.
      // This is a simple check to avoid re-copying if the source file is ALREADY in the target folder.
      // Note: makeCopy always creates a NEW file, so this doesn't prevent duplicate *copies* if run multiple times on same source.
      let isAlreadyInTarget = false;
      const parents = file.getParents();
      while(parents.hasNext()){
        if(parents.next().getId() === targetFolder.getId()){
          isAlreadyInTarget = true;
          break;
        }
      }

      if(isAlreadyInTarget){
        Logger.log(`File "${file.getName()}" is already in the target folder "${TARGET_FOLDER_NAME}". Skipping copy.`);
        // If you want to create a new copy even if an original is in the target folder, remove this check.
        // For now, we assume if the original is there, we don't need another copy from itself.
        // filesSkippedCount++; // Or handle as per desired logic
        // continue;
      }


      try {
        // Create a copy. Drive handles duplicate names in the target folder by appending (1), (2), etc.
        // We can also prefix the name.
        const newFileName = file.getName(); // Using original name. Or: `Copy of ${file.getName()}`
        const copiedFile = file.makeCopy(newFileName, targetFolder);
        Logger.log(`Successfully copied "${file.getName()}" to "${TARGET_FOLDER_NAME}" as "${copiedFile.getName()}" (New ID: ${copiedFile.getId()}).`);
        filesCopiedCount++;
      } catch (e) {
        Logger.log(`Error copying file "${file.getName()}": ${e.toString()}. This could be due to permissions or file type restrictions.`);
      }
    }

    // 4. Log summary and show a message to the user
    const summaryMessage = `Script finished.
Found: ${filesFoundCount} file(s).
Copied: ${filesCopiedCount} file(s).
Skipped: ${filesSkippedCount} file(s) (e.g., script file itself).
Files were copied to the folder: "${TARGET_FOLDER_NAME}".
Please check the logs for detailed information (View > Logs).`;

    Logger.log(summaryMessage);
    Browser.msgBox("Process Complete", summaryMessage, Browser.Buttons.OK);

  } catch (error) {
    Logger.log(`An unexpected error occurred in copyFilesWithKeyword: ${error.toString()} \nStack: ${error.stack}`);
    Browser.msgBox("Error", `An unexpected error occurred. Please check the logs for more details. Error: ${error.message}`, Browser.Buttons.OK);
  }
}

/**
 * Gets a Google Drive folder by its name. If it doesn't exist in the root, it creates it.
 * @param {string} folderName The name of the folder.
 * @return {GoogleAppsScript.Drive.Folder|null} The Folder object, or null if an error occurs.
 * @private
 */
function getOrCreateFolder_(folderName) {
  try {
    const folders = DriveApp.getFoldersByName(folderName);
    if (folders.hasNext()) {
      const folder = folders.next();
      Logger.log(`Folder "${folderName}" already exists with ID: ${folder.getId()}`);
      if (folders.hasNext()) {
        // This means multiple folders with the same name exist at the root or where DriveApp.getFoldersByName searches.
        // The script will use the first one found.
        Logger.log(`Warning: Multiple folders found with the name "${folderName}". Using the first one encountered.`);
      }
      return folder;
    } else {
      Logger.log(`Folder "${folderName}" not found at the root of your Drive. Creating it...`);
      const newFolder = DriveApp.createFolder(folderName);
      Logger.log(`Folder "${folderName}" created successfully with ID: ${newFolder.getId()}`);
      return newFolder;
    }
  } catch (e) {
    Logger.log(`Error in getOrCreateFolder_ for folder "${folderName}": ${e.toString()}`);
    // Browser.msgBox is avoided here to prevent issues if this function is called in a non-UI context later,
    // the main function will handle user notification.
    return null;
  }
}

/**
 * Adds a custom menu to the Google Sheet/Doc UI to run the script easily.
 * This function runs automatically when the file (Sheet/Doc) is opened.
 */
function onOpen() {
  // Use SpreadsheetApp.getUi() if script is bound to a Google Sheet
  // Use DocumentApp.getUi() if script is bound to a Google Doc
  // Use FormApp.getUi() if script is bound to a Google Form
  // For a standalone script, this menu won't appear unless you open it via a container.
  try {
    const ui = SpreadsheetApp.getUi(); // Assuming it's often used with Sheets
     ui.createMenu('Drive Utilities')
      .addItem('Copy "Knowledge Aura" Files', 'copyFilesWithKeyword')
      .addToUi();
  } catch (e) {
    // If not in a Spreadsheet, try DocumentApp. This is a common fallback.
    try {
        const ui = DocumentApp.getUi();
        ui.createMenu('Drive Utilities')
            .addItem('Copy "Knowledge Aura" Files', 'copyFilesWithKeyword')
            .addToUi();
    } catch (e2) {
        Logger.log("Could not create UI menu. This script might be standalone or in an unsupported environment for onOpen() UI creation: " + e2.message);
    }
  }
}
```