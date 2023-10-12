class Bezier:
    @staticmethod
    def lerp(p0, p1, t):
        ###線形補間（Linear Interpolation）関数
        return (1 - t) * p0 + t * p1

    @staticmethod
    def quadratic(p0, p1, p2, t):
        ###2次のベジェ曲線
        q0 = Bezier.lerp(p0, p1, t)
        q1 = Bezier.lerp(p1, p2, t)
        return Bezier.lerp(q0, q1, t)

    @staticmethod
    def cubic(p0, p1, p2, p3, t):
        ###3次のベジェ曲線###
        q0 = Bezier.lerp(p0, p1, t)
        q1 = Bezier.lerp(p1, p2, t)
        q2 = Bezier.lerp(p2, p3, t)
        r0 = Bezier.lerp(q0, q1, t)
        r1 = Bezier.lerp(q1, q2, t)
        return Bezier.lerp(r0, r1, t)
