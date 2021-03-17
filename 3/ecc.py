from unittest import TestCase

class FieldElement:

	def __init__(self, num, prime):
		if num >= prime or num < 0:
			error = 'Num {} not in field range 0 to {}'.format(
				num, prime-1)
			raise ValueError(error)
		self.num = num
		self.prime = prime

	def __repr__(self):
		return 'FieldElement_{}({})'.format(self.prime, self.num)

	def __eq__(self,other):
		if other is None:
			return False
		return self.num == other.num and self.prime == other.prime

	def __ne__(self,other):
		return not (self == other)

	def __add__(self,other):
		if self.prime != other.prime:
			#同じ有限体でなければ計算不能
			raise TypeError('Cannot add two numbers in different fields')
		num = (self.num + other.num) % self.prime
		#クラスのインスタンスを返す
		return self.__class__(num,self.prime)

	def __sub__(self,other):
		if self.prime != other.prime:
			raise TypeError('Cannot substract two number in different fields')
		num = (self.num - other.num) % self.prime
		return self.__class__(num,self.prime)

	def __mul__(self,other):
		if self.prime != other.prime:
			raise TypeError('Cannot multiply two number in different fields')
		num = (self.num * other.num) % self.prime
		return self.__class__(num,self.prime)

	def __pow__(self,exponent):
		#指数を0 ~ p-2の範囲内にする
		n = exponent % (self.prime - 1)
		num = pow(self.num,n,self.prime)
		return self.__class__(num,self.prime)

	def __truediv__(self,other):
		if self.prime != other.prime:
			raise TypeError('Cannot divide two number in different fields')
		#フェルマーの小定理「n^(p-1) % p == 1」より、「1/n = pow(n,p-2,p)」が成立
		num = (self.num * pow(other.num, self.prime-2, self.prime) % self.prime)
		return self.__class__(num,self.prime)
	
	#int * FieldElement
	def __rmul__(self, coefficient):
		num = (self.num * coefficient) % self.prime
		return self.__class__(num=num, prime=self.prime)



class Point:

	def __init__(self,x,y,a,b):
		self.a = a
		self.b = b
		self.x = x
		self.y = y
		#無限遠点の場合
		if self.x is None and self.y is None:
			return
		#与えられた点が楕円曲線上にあるかを判定
		if self.y**2 != self.x**3 + a * x + b:
			raise ValueError('({},{}) is not on the curve'.format(x,y))

	def __repr__(self):
		if self.x is None:
			return 'Point(infinity)'
		elif isinstance(self.x, FieldElement):
			return 'Point({},{})_{}_{} FieldElement({})'.format(
				self.x.num, self.y.num, self.a.num, self.b.num, self.x.prime)
		else:
			return 'Point({},{})_{}_{}'.format(self.x, self.y, self.a, self.b)


	def __eq__(self,other):
		#同じ曲線上かつ同じ点であるかを判定
		return self.x == other.x and self.y == other.y \
			and self.a == other.a and self.b == other.b

	def __ne__(self,other):
		return not (self == other)

	def __add__(self,other):
		if self.a != other.a or self.b != other.b:
			raise TypeError('Points {}, {} are not on the same curve'.format(self,other))

		#self,otherが無限遠点の場合、それらは加法単位元であるのでother,selfを返す
		if self.x is None:
			return other

		if other.x is None:
			return self

		#2つの点が加法逆元(xが同じ、yが異なる)の場合、無限遠点を返す
		if self.x == other.x and self.y != other.y:
			return self.__class__(None,None,self.a,self.b)

		#根と係数の関係よりP3の式を導出出来る
		if self.x != other.x:
			s = (other.y - self.y) / (other.x - self.x)
			x = s**2 - self.x - other.x
			y = s * (self.x - x) - self.y
			return self.__class__(x,y,self.a,self.b)

		#接線が垂直線 →  2つの点が等しく、y座標が0
		if self == other and self.y == 0 * self.x:
			return self.__class__(None,None,self.a,self,b)

		if self == other:
			#sは微分によって求められた傾き
			s = (3 * (self.x**2) + self.a) / (2 * self.y)
			x = s**2 - 2 * self.x
			y = s * (self.x - x) - self.y
			return self.__class__(x, y, self.a, self.b)

	#2進展開	
	def __rmul__(self, coefficient):
		coef = coefficient
		current = self
		result = self.__class__(None, None, self.a, self.b)
		while coef:
			#lsbが1であれば、現在のビットを加算
			if coef & 1:
				result += current
			#係数の最大値を超えるまで点を2倍
			current += current
			#右シフト
			coef >>= 1
		return result


class ECCTest(TestCase):
	
	def test_on_curve(self):
		prime = 223
		a = FieldElement(0,prime)
		b = FieldElement(7,prime)
		valid_points = ((192,105),(17,56),(1,193))
		invalid_points = ((200,119),(42,99))
		for x_raw, y_raw in valid_points:
			x = FieldElement(x_raw, prime)
			y = FieldElement(y_raw, prime)
			Point(x,y,a,b)
		
		for x_raw, y_raw in invalid_points:
			x = FieldElement(x_raw,prime)
			y = FieldElement(y_raw,prime)
			with self.assertRaises(ValueError):
				Point(x,y,a,b)
	
	def test_add(self):
		prime = 223
		a = FieldElement(0,prime)
		b = FieldElement(7,prime)

		additions = (
			(192,105,17,56,170,142),
			(47,71,117,141,60,139),
			(142,98,76,66,47,71),
		)

		for x1_raw, y1_raw, x2_raw, y2_raw, x3_raw, y3_raw in additions:
			x1 = FieldElement(x1_raw,prime)
			y1 = FieldElement(y1_raw,prime)
			p1 = Point(x1, y1, a, b)
			x2 = FieldElement(x2_raw,prime)
			y2 = FieldElement(y2_raw,prime)
			p2 = Point(x1, y1, a, b)
			x3 = FieldElement(x3_raw,prime)
			y3 = FieldElement(y3_raw,prime)
			p3 = Point(x1, y1, a, b)
			self.assertEqual(p1 + p2, p3)

#secp256k1専用の体を定義するためのパラメーター
A = 0
B = 7
P = 2**256 - 2**32 - 977
N = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141

class S256Field(FieldElement):

	def __init__(self,num,prime=None):
		super().__init__(num=num, prime=P)
	
	def __repr__(self):
		#0埋めして64bitにする
		return '{:x}'.format(self.num).zfill(64)


class S256Point(Point):

	def __init__(self, x, y, a=None, b=None):
		a, b = S256Field(A), S256Field(B)
		if type(x) == int:
			super().__init__(x=S256Field(x), y=S256Field(y), a=a, b=b)
		else:
			#無限遠点で初期化する場合、xとyはクラスを経由せずに直接渡す
			super().__init__(x=x, y=y, a=a, b=b)
	
	def __repr__(self):
		if self.x is None:
			return 'S256Point(infinity)'
		else:
			return 'S256Point({}, {})'.format(self.x, self.y)

	def __rmul__(self, coefficient):
		#nG = 0のため、nでmodを取る。これでn回ごとに無限遠点に戻ることが可能
		coef = coefficient % N
		return super().__rmul__(coef)
	
	def verify(self, z, sig):
		s_inv = pow(sig.s, N - 2, N)
		u = z * s_inv % N
		v = sig.r * s_inv % N
		total = u * G + v * self
		return total.x.num == sig.r

	

G = S256Point(
    0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798,
    0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8)

class Signature:

	def __init__(self, r, s):
		self.r = r
		self.s = s

	def __repr__(self):
		return 'Signature({:x},{:x})'.format(self.r, self.s)


class PrivateKey:

	def __init__(self, secret):
		self.secret = secret
		self.point = secret * G  # <1>

	def hex(self):
		return '{:x}'.format(self.secret).zfill(64)
    
	def sign(self, z):
		k = self.deterministic_k(z)  # <1>
		r = (k * G).x.num
		k_inv = pow(k, N - 2, N)
		s = (z + r * self.secret) * k_inv % N
		if s > N / 2:
			s = N - s
		return Signature(r, s)

	def deterministic_k(self, z):
		k = b'\x00' * 32
		v = b'\x01' * 32
		if z > N:
			z -= N
		z_bytes = z.to_bytes(32, 'big')
		secret_bytes = self.secret.to_bytes(32, 'big')
		s256 = hashlib.sha256
		k = hmac.new(k, v + b'\x00' + secret_bytes + z_bytes, s256).digest()
		v = hmac.new(k, v, s256).digest()
		k = hmac.new(k, v + b'\x01' + secret_bytes + z_bytes, s256).digest()
		v = hmac.new(k, v, s256).digest()
		while True:
			v = hmac.new(k, v, s256).digest()
			candidate = int.from_bytes(v, 'big')
			if candidate >= 1 and candidate < N:
				return candidate  # <2>
			k = hmac.new(k, v + b'\x00', s256).digest()
			v = hmac.new(k, v, s256).digest()


