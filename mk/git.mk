# Define the variables for Git username and email
GIT_USERNAME = jcbowyer
GIT_EMAIL = jcbowyer@hotmail.com

# Target to set Git username and email
git-set-config:
	@echo "Setting Git username to $(GIT_USERNAME) and email to $(GIT_EMAIL)"
	git config --global user.name "$(GIT_USERNAME)"
	git config --global user.email "$(GIT_EMAIL)"
	@echo "Git username and email have been set successfully!"
