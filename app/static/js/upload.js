/**
 * Sets up an event listener for the "htmx:afterRequest" event on the upload-files-table element.
 * When triggered, it checks if the event target is a file download button and initiates a file download.
 * function
 * listens htmx:afterRequest
 * returns {void}
 */
document.addEventListener("DOMContentLoaded", function () {
  document
    .getElementById("upload-files-table")
    .addEventListener("htmx:afterRequest", function (evt) {
      if (evt.target && evt.target.id === "file-download-button") {
        const downloadUrl = evt.target.getAttribute("hx-get");
        const a = document.createElement("a");
        a.href = downloadUrl;
        a.download = ""; // Optional: specify a filename if needed
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
      }
    });
});

/**
 * Listens for the "showAlert" event on the document.body and updates the data of the "upload-page" component accordingly.
 * If the event detail has a "type" property of "updated", "added", or "deleted",
 * it sets the corresponding data properties on the "upload-page" component.
 * The data properties set are "isUpdated", "isAdded", and "isDeleted" respectively, and the "message" property is set to the value of the "message" property in the event detail.
 * If the "upload-page" component is not found, an error is logged to the console.
 */
document.body.addEventListener("showAlert", function (evt) {
  try {
    console.log("showAlert event received");
    const source = evt.detail.source;
    const components = document.querySelectorAll("[x-data]");

    const uploadPageIndex = Array.from(components).findIndex(
      (component) => component.id === source
    );

    if (uploadPageIndex === -1) {
      throw new Error("No element with id 'upload-page' found");
    }
    const component = components[uploadPageIndex];
    if (!component) {
      throw new Error("No element with x-data found");
    }
    const data = Alpine.mergeProxies(component._x_dataStack);
    setTimeout(function () {
      if (evt.detail.type == "updated") {
        data.isUpdated = true;
        data.message = evt.detail.message;
      } else if (evt.detail.type == "added") {
        data.isAdded = true;
        data.message = evt.detail.message;
      } else if (evt.detail.type == "deleted") {
        data.isDeleted = true;
        data.message = evt.detail.message;
      }
    }, 1000);
  } catch (error) {
    console.error("Error in message display:", error);
  }
});

// Making a after request function to call and handle the loading state
function handleUploadRequest() {
  try {
    console.log("handleUploadRequest called");
    const components = document.querySelectorAll("[x-data]");

    const uploadPageIndex = Array.from(components).findIndex(
      (component) => component.id === "upload-page"
    );

    if (uploadPageIndex === -1) {
      throw new Error("No element with id 'upload-page' found");
    }
    const component = components[uploadPageIndex];
    if (!component) {
      throw new Error("No element with x-data found");
    }
    const data = Alpine.mergeProxies(component._x_dataStack);
    console.log(
      data.isLoading,
      "isLoading State",
      data.fileLoaded,
      "fileLoaded State"
    );
    data.isLoading = false;
    data.fileLoaded = false;
    data.fileName = "";

    console.log(
      data.isLoading,
      "isLoading State after Function Call",
      data.fileLoaded,
      "fileLoaded State after Function Call"
    );
  } catch (error) {
    console.error("Error in click event handler:", error);
  }
}
