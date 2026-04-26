import re

with open('c:/Users/Admin/Desktop/Ecommerc/backend/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# The corrupted section starts after the create_new_tax_rule function
# and includes mangled update/delete tax rule functions

pattern = r'''(    return db_tax\n)(    current_user: User = Depends\(get_current_admin_user\),\n    db: Session = Depends\(get_db\)\n\):\n    """Update a tax rule \(admin only\)"""\n    db_tax = update_tax_rule\(db, tax_id, update\)\n    if not db_tax:\n        raise HTTPException\(status_code=404, detail="Tax rule not found"\)\n    log_audit_action\(db, current_user\.id, "UPDATE", "TaxRule", db_tax\.id, f"Updated tax rule \{db_tax\.name\}"\)\n    return db_tax\n\n\n@app\.delete\("/api\n\n\n@app\.delete\("/api/admin/tax-rules/\{tax_id\}", response_model=Message, tags=\["Admin"\]\)/admin/tax-rules/\{tax_id\}", response_model=Message, tags=\["Admin"\]\)\ndef delete_existing_tax_rule\(def delete_existing_tax_rule\(\n    tax_id: int,    tax_id: int,\n    current_user: User = Depends\(get_current_admin_user\),\n    db: Session = Depends\(get_db\)\n\):\n    """Delete a tax rule \(admin only\)"""\n    success = delete_tax_rule\(db, tax_id\)\n    if not success:\n        raise HTTPException\(status_code=404, detail="Tax rule not found"\)\n    log_audit_action\(db, current_user\.id, "DELETE", "TaxRule", tax_id, "Deleted tax rule"\)\n    return \{"message": "Tax rule deleted"\})'''

replacement = r'''\1

@app.put("/api/admin/tax-rules/{tax_id}", response_model=TaxRuleResponse, tags=["Admin"])
def update_existing_tax_rule(
    tax_id: int,
    update: TaxRuleUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update a tax rule (admin only)"""
    db_tax = update_tax_rule(db, tax_id, update)
    if not db_tax:
        raise HTTPException(status_code=404, detail="Tax rule not found")
    log_audit_action(db, current_user.id, "UPDATE", "TaxRule", db_tax.id, f"Updated tax rule {db_tax.name}")
    return db_tax


@app.delete("/api/admin/tax-rules/{tax_id}", response_model=Message, tags=["Admin"])
def delete_existing_tax_rule(
    tax_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete a tax rule (admin only)"""
    success = delete_tax_rule(db, tax_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tax rule not found")
    log_audit_action(db, current_user.id, "DELETE", "TaxRule", tax_id, "Deleted tax rule")
    return {"message": "Tax rule deleted"}'''

new_content, count = re.subn(pattern, replacement, content)

if count > 0:
    with open('c:/Users/Admin/Desktop/Ecommerc/backend/main.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f'Fixed successfully ({count} replacement)')
else:
    print('Regex did not match. Dumping relevant section...')
    idx = content.rfind('Created tax rule')
    if idx != -1:
        print(repr(content[idx-100:idx+1200]))

