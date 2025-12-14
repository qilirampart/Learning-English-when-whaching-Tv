"""从数据库中删除指定单词"""
import sys
sys.path.insert(0, 'backend')

from app import create_app, db
from app.models.word import Word

app = create_app()

with app.app_context():
    word_text = "monkey"

    word = Word.query.filter_by(word=word_text).first()

    if word:
        print(f"找到单词: {word.word}")
        print(f"  音标: {word.phonetic}")
        print(f"  翻译: {word.translation}")
        print(f"  释义: {word.definition}")
        print()

        confirm = input(f"确认删除单词 '{word_text}' 吗? (y/n): ")
        if confirm.lower() == 'y':
            db.session.delete(word)
            db.session.commit()
            print(f"✓ 已删除单词 '{word_text}'")
            print("提示: 现在重新查询这个单词时会调用有道API获取最新数据")
        else:
            print("取消删除")
    else:
        print(f"数据库中没有找到单词 '{word_text}'")
