"""Assert permissions and verify live revocation. Restores revoked group in finally."""
from common import connect, TENANT

def visible(doc_id,user_id):
    with connect() as db:
        with db.transaction():
            db.execute('SELECT set_config(%s,%s,true)',('app.user_id',user_id))
            db.execute('SELECT set_config(%s,%s,true)',('app.tenant_id',TENANT))
            return db.execute('SELECT EXISTS(SELECT 1 FROM raglab.chunks WHERE document_id=%s)',(doc_id,)).fetchone()[0]

def check(label,actual,expected):
    print(('PASS' if actual==expected else 'FAIL')+f'  {label} => {actual}')
    if actual!=expected: raise AssertionError(label)

def main():
    check('Priya reads HR-001',visible('HR-001','priya'),True)
    check('Arjun blocked from HR-001',visible('HR-001','arjun'),False)
    check('Arjun reads FINANCE-001',visible('FINANCE-001','arjun'),True)
    check('Divya reads FINANCE-001',visible('FINANCE-001','divya'),True)
    check('Meena blocked from FINANCE-001',visible('FINANCE-001','meena'),False)
    check('Unknown identity blocked',visible('HR-001','unknown-person'),False)
    check('Arjun sees HR-046 (shared with all)',visible('HR-046','arjun'),True)
    with connect(admin=True) as db:
        db.execute("DELETE FROM raglab.user_groups WHERE user_id='arjun' AND group_name='FINANCE'")
        db.commit()
    try:
        check('Arjun denied FINANCE-001 after revocation',visible('FINANCE-001','arjun'),False)
    finally:
        with connect(admin=True) as db:
            db.execute("INSERT INTO raglab.user_groups(user_id,group_name) VALUES('arjun','FINANCE') ON CONFLICT DO NOTHING")
            db.commit()
    check('Arjun regains FINANCE-001 after restore',visible('FINANCE-001','arjun'),True)
    with connect() as db:
        try:
            db.execute('SELECT * FROM raglab.document_acl LIMIT 1').fetchall()
        except Exception:
            print('PASS  Direct access to ACL table denied')
        else:
            raise AssertionError('ACL table unexpectedly readable by restricted role')
    print('ALL CHECKS PASSED. Classroom user IDs are simulated; production requires verified authentication.')

if __name__=='__main__': main()
