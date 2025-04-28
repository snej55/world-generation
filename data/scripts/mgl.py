import moderngl, array, pygame

default_vert = """
#version 330 core

in vec2 vert;
in vec2 texcoord;
out vec2 uvs;

void main() {
    uvs = texcoord;
    gl_Position = vec4(vert.x, vert.y, 0.0, 1.0);
}
"""

default_frag = """
#version 330 core

uniform sampler2D tex;

in vec2 uvs;
out vec4 f_color;

void main() {
    f_color = vec4(texture(tex, uvs).rgb, 1.0);
}
"""

def read_f(path):
    f = open(path, 'r')
    data = f.read()
    f.close()
    return data

class MGL:
    def __init__(self):
        self.ctx = moderngl.create_context(require=330)
        self.quad_buffer = self.ctx.buffer(data=array.array('f', [
            # position (x, y) , texture coordinates (x, y)
            -1.0, 1.0, 0.0, 0.0,
            -1.0, -1.0, 0.0, 1.0,
            1.0, 1.0, 1.0, 0.0,
            1.0, -1.0, 1.0, 1.0,
        ]))
        self.quad_buffer_notex = self.ctx.buffer(data=array.array('f', [
            # position (x, y)
            -1.0, 1.0,
            -1.0, -1.0,
            1.0, 1.0,
            1.0, -1.0,
        ]))
        self.default_frag = default_frag
        self.default_vert = default_vert
    
    def default_ro(self):
        return RenderObject(self, self.default_frag, default_ro=True)
    
    def render_object(self, frag_path, vert_shader=None, vao_args=['2f 2f', 'vert', 'texcoord'], buffer=None):
        frag_shader = read_f(frag_path)
        if vert_shader:
            vert_shader = read_f(vert_shader)
        return RenderObject(self, frag_shader, vert_shader=vert_shader, vao_args=vao_args, buffer=buffer)
    
    @staticmethod
    def texture_update(tex, surf):
        tex.write(surf.get_view('1'))
        return tex

    def surf_to_texture(self, surf):
        tex = self.ctx.texture(surf.get_size(), 4)
        tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
        tex.swizzle = 'BGRA'
        tex.write(surf.get_view('1'))
        return tex
    
    def texture_to_surf(self, texture, dim, mode='RGBA'):
        return pygame.image.frombytes(texture.read(), dim, mode)

class RenderObject:
    def __init__(self, mgl, frag_shader, vert_shader=None, vao_args=['2f 2f', 'vert', 'texcoord'], buffer=None, default_ro=False):
        self.mgl = mgl
        self.ctx = mgl.ctx
        self.default_ro = default_ro
        self.vert_shader = vert_shader
        if not vert_shader:
            self.vert_shader = default_vert
        self.frag_shader = frag_shader
        self.vao_args = vao_args
        self.program = self.ctx.program(vertex_shader=self.vert_shader, fragment_shader=self.frag_shader)
        if not buffer:
            buffer = self.mgl.quad_buffer
        self.vao = self.mgl.ctx.vertex_array(self.program, [(buffer, *vao_args)])
        self.temp_texs = []

    def parse_uniforms(self, uniforms):
        for name, value in uniforms.items():
            if type(value) == pygame.Surface:
                tex = self.mgl.surf_to_texture(value)
                uniforms[name] = tex
                self.temp_texs.append(tex)
        return uniforms
    
    def update(self, uniforms={}):
        tex_id = 0
        uniform_list = list(self.program)
        for uniform in uniforms:
            if uniform in uniform_list:
                if type(uniforms[uniform]) == moderngl.Texture:
                    uniforms[uniform].use(tex_id)
                    self.program[uniform].value = tex_id
                    tex_id += 1
                    self.temp_texs.append(uniforms[uniform])
                else:
                    self.program[uniform].value = uniforms[uniform]

    def render(self, dest=None, uniforms={}):
        if not dest:
            dest = self.mgl.ctx.screen
            
        dest.use()
        uniforms = self.parse_uniforms(uniforms)
        self.update(uniforms=uniforms)
        self.vao.render(mode=moderngl.TRIANGLE_STRIP)
        
        for tex in self.temp_texs:
            tex.release()
        self.temp_texs = []