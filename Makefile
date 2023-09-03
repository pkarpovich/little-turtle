backup_db:
	sh ./scripts/backup.sh

apply_db_backup:
	sh ./scripts/apply_backup_to_mongo.sh

setup_db_backup:
	sh ./scripts/setup_backup.sh

deploy_local:
	spot -t local -v -i ./inventory.yml -k ~/.ssh/id_pi_ed25519