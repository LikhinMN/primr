ADDON_DIR = primr
ZIP_NAME = primr.zip
BLENDER_ADDONS = ~/.config/blender/5.1/extensions/user_default

.PHONY: zip clean install

zip:
	rm -f $(ZIP_NAME)
	zip -r $(ZIP_NAME) $(ADDON_DIR)/

clean:
	rm -f $(ZIP_NAME)

install: zip
	cp $(ZIP_NAME) $(BLENDER_ADDONS)/