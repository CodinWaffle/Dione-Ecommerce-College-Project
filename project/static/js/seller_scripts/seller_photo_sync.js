/**
 * Synchronize photos between profile tab and store tab
 * @param {string} type - Either 'profile' or 'cover'
 * @param {string} photoUrl - URL of the uploaded photo (optional)
 */
function syncPhotoBetweenTabs(type, photoUrl = "") {
  if (type === "profile") {
    // Update both profile photo previews
    const profilePhotoPreview = document.getElementById(
      "profile-photo-preview"
    );
    const storePhotoPreview = document.getElementById("store-photo-preview");

    const imageUrl =
      profilePhotoPreview?.style.backgroundImage ||
      storePhotoPreview?.style.backgroundImage ||
      (photoUrl ? `url('${photoUrl}')` : "");

    if (profilePhotoPreview && imageUrl) {
      profilePhotoPreview.style.backgroundImage = imageUrl;
    }

    if (storePhotoPreview && imageUrl) {
      storePhotoPreview.style.backgroundImage = imageUrl;
    }
  } else if (type === "cover") {
    // Update both cover photo previews
    const coverPhotoPreview = document.getElementById("cover-photo-preview");
    const storeCoverPhotoPreview = document.getElementById(
      "store-cover-photo-preview"
    );

    const imageUrl =
      coverPhotoPreview?.style.backgroundImage ||
      storeCoverPhotoPreview?.style.backgroundImage ||
      (photoUrl ? `url('${photoUrl}')` : "");

    if (coverPhotoPreview && imageUrl) {
      coverPhotoPreview.style.backgroundImage = imageUrl;
    }

    if (storeCoverPhotoPreview && imageUrl) {
      storeCoverPhotoPreview.style.backgroundImage = imageUrl;
    }
  }
}
