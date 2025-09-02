"""
占い師データモデル
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class Fortuneteller:
    """占い師データモデル"""
    id: Optional[int] = None
    name: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    description: str = ""
    contact: str = ""
    category: str = ""
    status: str = "pending"
    submitted_by: str = "不明"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None
    website: Optional[str] = None
    zipcode: Optional[str] = None  # 郵便番号フィールド追加
    address: Optional[str] = None  # 住所フィールド追加

    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {k: v for k, v in self.__dict__.items() if v is not None}

    def validate(self) -> bool:
        """バリデーション"""
        if not self.name:
            return False
        if not (-90 <= self.latitude <= 90):
            return False
        if not (-180 <= self.longitude <= 180):
            return False

        # 郵便番号のバリデーション（任意フィールドなので、値があれば検証）
        if self.zipcode and not self._validate_zipcode(self.zipcode):
            return False

        return True

    def _validate_zipcode(self, zipcode: str) -> bool:
        """郵便番号の形式チェック（日本の郵便番号形式）"""
        import re
        # 日本の郵便番号形式：1234567 または 123-4567
        pattern = r'^(\d{7}|\d{3}-\d{4})$'
        return bool(re.match(pattern, zipcode))
