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
		if self.x == None
			return 'Point(Infinity)'
		else:
			return 'Point({},{})_{}_{}'.format(self.x, self.y, self.a, self.b)

	def __eq__(self,other):
		#同じ曲線上かつ同じ点であるかを判定
		return self.x == other.x and self.y == other.y \
			and self.a == other.a and self.b == other.b

	def __ne__(self,other):
		raise NotImplementedError

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

		if self == other:
			#sは微分によって求められた傾き
			s = (3 * self.x**2 + self.a) / (2 * self.y)
			x = s**2 - (2*self.x)
			y = s*(self.x - x) - self.y
			return self.__class__(x,y,self.a,self.b)

		#接線が垂直線 →  2つの点が等しく、y座標が0
		if self == other and self.y == 0 * self.x:
			return self.__class__(None,None,self.a,self,b)


