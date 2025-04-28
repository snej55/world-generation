#version 330 core

uniform sampler2D tex;
uniform sampler2D light;

in vec2 uvs;
out vec4 f_color;

vec4 gaussKernel3x3[9];

void main() {
    gaussKernel3x3[0] = vec4(-1.0, -1.0, 0.0,  1.0 / 16.0);
    gaussKernel3x3[1] = vec4(-1.0,  0.0, 0.0,  2.0 / 16.0);
    gaussKernel3x3[2] = vec4(-1.0, +1.0, 0.0,  1.0 / 16.0);
    gaussKernel3x3[3] = vec4( 0.0, -1.0, 0.0,  2.0 / 16.0);
    gaussKernel3x3[4] = vec4( 0.0,  0.0, 0.0,  4.0 / 16.0);
    gaussKernel3x3[5] = vec4( 0.0, +1.0, 0.0,  2.0 / 16.0);
    gaussKernel3x3[6] = vec4(+1.0, -1.0, 0.0,  1.0 / 16.0);
    gaussKernel3x3[7] = vec4(+1.0,  0.0, 0.0,  2.0 / 16.0);
    gaussKernel3x3[8] = vec4(+1.0, +1.0, 0.0,  1.0 / 16.0);
    
    vec2 texelSize = vec2(1.0) / textureSize(light, 0) * 4.0;

    vec4 color = vec4(0.0);
    for (int i = 0; i < gaussKernel3x3.length(); ++i)
        color += gaussKernel3x3[i].w * texture(light, uvs.xy + texelSize * gaussKernel3x3[i].xy);
    f_color = texture(tex, uvs.xy) - color;
}