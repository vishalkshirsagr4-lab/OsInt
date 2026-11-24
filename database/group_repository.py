

def add_or_update_group(group_id, group_title):
    local_conn = sqlite3.connect('bot.db', timeout=15)
    local_c = local_conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        # Check if group already exists
        local_c.execute("SELECT group_id FROM bot_groups WHERE group_id=?", (group_id,))
        exists = local_c.fetchone()
        if exists:
            # Only update title and last_active — DO NOT touch feature settings!
            local_c.execute(
                "UPDATE bot_groups SET group_title=?, last_active=? WHERE group_id=?",
                (group_title, now, group_id)
            )
        else:
            # New group — insert with all defaults
            local_c.execute(
                "INSERT INTO bot_groups (group_id, group_title, added_date, last_active) VALUES (?, ?, ?, ?)",
                (group_id, group_title, now, now)
            )
        local_conn.commit()
    except Exception as e:
        print(f"Error adding group: {e}")
    finally:
        local_conn.close()


def remove_group(group_id):
    local_conn = sqlite3.connect('bot.db', timeout=15)
    local_c = local_conn.cursor()
    try:
        local_c.execute("DELETE FROM bot_groups WHERE group_id=?", (group_id,))
        local_conn.commit()
    except Exception as e:
        print(f"Error removing group: {e}")
    finally:
        local_conn.close()


def get_group_settings(group_id):
    local_conn = sqlite3.connect('bot.db', timeout=15)
    local_c = local_conn.cursor()
    local_c.execute('''
        SELECT number_info_enabled, userid_info_enabled,
               username_info_enabled, aadhar_info_enabled, instagram_info_enabled,
               ifsc_info_enabled, vehicle_info_enabled, welcome_enabled,
               welcome_message, welcome_rules, goodbye_enabled, goodbye_message,
               welcome_photo_file_id,
               COALESCE(gst_info_enabled, 1), COALESCE(email_info_enabled, 1),
               COALESCE(pan_info_enabled, 1), COALESCE(pak_num_info_enabled, 1),
               COALESCE(ff_info_enabled, 1), COALESCE(pincode_info_enabled, 1),
               COALESCE(hitek_info_enabled, 1), COALESCE(tg_bomber_enabled, 1),
               COALESCE(bomber_enabled, 1), COALESCE(free_info_mode, 0)
        FROM bot_groups WHERE group_id=?
    ''', (group_id,))
    result = local_c.fetchone()
    local_conn.close()
    if result:
        return {
            'number': result[0],
            'userid': result[1],
            'username': result[2],
            'aadhar': result[3],
            'instagram': result[4],
            'ifsc': result[5],
            'vehicle': result[6],
            'welcome_enabled': result[7],
            'welcome_message': result[8],
            'welcome_rules': result[9],
            'goodbye_enabled': result[10] if result[10] is not None else 1,
            'goodbye_message': result[11] if result[11] else '💥 Arre {name} chala gaya!\n━━━━━━━━━━━━━━━━━━\n🗓️ Left Date: {date}\n⏰ Left Time: {time} (IST)\n😤 {group} ke baad kahan jayega?\n🤧 Ruk tere par bomber pelta hun!\n━━━━━━━━━━━━━━━━━━',
            'welcome_photo_file_id': result[12],
            'gst': result[13],
            'email': result[14],
            'pan': result[15],
            'pak_num': result[16],
            'ff': result[17],
            'pincode': result[18],
            'hitek': result[19],
            'tg_bomber': result[20],
            'bomber': result[21],
            'free_info_mode': result[22] if len(result) > 22 and result[22] is not None else 0,
        }
    else:
        # Default all enabled
        return {
            'number': 1, 'userid': 1, 'username': 1, 'aadhar': 1,
            'instagram': 1, 'ifsc': 1, 'vehicle': 1, 'gst': 1,
            'email': 1, 'pan': 1, 'pak_num': 1, 'ff': 1,
            'pincode': 1, 'hitek': 1, 'tg_bomber': 1, 'bomber': 1,
            'free_info_mode': 0,
            'welcome_enabled': 1, 'goodbye_enabled': 1,
            'goodbye_message': '💥 Arre {name} chala gaya!\n━━━━━━━━━━━━━━━━━━\n🗓️ Left Date: {date}\n⏰ Left Time: {time} (IST)\n😤 {group} ke baad kahan jayega?\n🤧 Ruk tere par bomber pelta hun!\n━━━━━━━━━━━━━━━━━━',
            'welcome_photo_file_id': None,
            'welcome_message': '👋 Welcome {name}\n🎉 Welcome To {group}\n📌 This group is Backup Group of Info Bot 🤖\n📅 Date: {date}\n⏰ Time: {time}\n🌍 Language: -\n⚠️ Please Follow All Group Rules\n📜 Rules: {rules}\n🚀 Enjoy Your Stay In 📊',
            'welcome_rules': ''
        }

def set_group_feature(group_id, feature, enabled):
    local_conn = sqlite3.connect('bot.db', timeout=15)
    local_c = local_conn.cursor()
    feature_map = {
        'number':    'number_info_enabled',
        'userid':    'userid_info_enabled',
        'username':  'username_info_enabled',
        'aadhar':    'aadhar_info_enabled',
        'instagram': 'instagram_info_enabled',
        'ifsc':      'ifsc_info_enabled',
        'vehicle':   'vehicle_info_enabled',
        'gst':       'gst_info_enabled',
        'email':     'email_info_enabled',
        'pan':       'pan_info_enabled',
        'pak_num':   'pak_num_info_enabled',
        'ff':        'ff_info_enabled',
        'pincode':   'pincode_info_enabled',
        'hitek':     'hitek_info_enabled',
        'tg_bomber': 'tg_bomber_enabled',
        'bomber':    'bomber_enabled',
        'welcome_enabled': 'welcome_enabled',
        'goodbye_enabled': 'goodbye_enabled',
        'free_info_mode':  'free_info_mode',
    }
    col = feature_map.get(feature)
    if not col:
        return False
    try:
        local_c.execute("BEGIN")
        local_c.execute(
            "INSERT OR IGNORE INTO bot_groups (group_id, group_title) VALUES (?, ?)",
            (group_id, "Unknown")
        )
        local_c.execute(f"UPDATE bot_groups SET {col}=? WHERE group_id=?", (1 if enabled else 0, group_id))
        local_conn.commit()
        trigger_backup_soon()
        return True
    except Exception as e:
        try: local_conn.rollback()
        except Exception: pass
        print(f"Error setting group feature: {e}")
        return False
    finally:
        local_conn.close()

def get_all_groups():
    local_conn = sqlite3.connect('bot.db', timeout=15)
    local_c = local_conn.cursor()
    local_c.execute("SELECT group_id, group_title, added_date, last_active FROM bot_groups ORDER BY added_date DESC")
    groups = local_c.fetchall()
    local_conn.close()
    return groups
