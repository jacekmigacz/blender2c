bl_info = {
    'name': "Export C header for OpenGL ES (.h)",
    'author': "Jacek Migacz",
    'version': (0, 1),
    'blender': (2, 5, 0),
    'location': "File > Export > C header for OpenGL ES (.h)",
    'description': "Exports meshes to the C header for OpenGL ES (.h).",
    'warning': "",
    'wiki_url': "",
    'tracker_url': "",
    'category': "Import-Export"
}

import getopt, os, sys
import bpy
from bpy.props import StringProperty
from bpy_extras.io_utils import ExportHelper

indent = "    "

class Export_C(bpy.types.Operator, ExportHelper):
    bl_idname = "export_scene.c"
    bl_label = "Export C/OpenGL ES"
    bl_options = {'PRESET'}

    filename_ext = ".h"
    filter_glob = StringProperty(default="*.h", options={'HIDDEN'})

    def execute(self, context):
        global indent

        ctx = bpy.context
        sc = ctx.scene

        self.parse_args()
        if self.outfile == "":
            basename = bpy.path.basename(bpy.context.blend_data.filepath)
            basename = os.path.splitext(basename)[0]
            self.outfile = "{0}.h".format(basename)

        f = open(self.outfile, "w", encoding="utf8", newline="\n")
        fw = f.write

        objs = [obj for obj in sc.objects if obj.type == 'MESH']
        for obj in objs:
            mesh = obj.to_mesh(sc, True, 'PREVIEW')
            uvertices = []
            indicies = []
            for face in mesh.tessfaces:
                accumulator = []
                for n, i in enumerate(face.vertices):
                    if (face.use_smooth):
                        vertex = mesh.vertices[i].co, mesh.vertices[i].normal
                    else:
                        vertex = mesh.vertices[i].co, face.normal
                    try:
                        j = uvertices.index(vertex)
                    except:
                        uvertices.append(vertex)
                        j = len(uvertices) - 1

                    indicies.append(j)
                    if len(face.vertices) == 4:
                        if n == 0:
                            accumulator.append(j)
                        if n == 2:
                            accumulator.append(j)
                        if n == 3:
                            indicies.append(accumulator[0])
                            indicies.append(accumulator[1])

            fw("static const struct vertex_pn %s_vertices[] = {\n" % obj.name)
            for v in uvertices:
                fw("%s{{ " % indent)
                fw("{:9.6f}, {:9.6f}, {:9.6f}".format(v[0][0], v[0][1], v[0][2]))
                fw(" }, { ")
                fw("{:9.6f}, {:9.6f}, {:9.6f}".format(v[1][0], v[1][1], v[1][2]))
                fw(" }},\n")
            fw("};\n\n")

            fw("static const unsigned char %s_indicies[] = {\n" % obj.name)
            for n, i in enumerate(indicies):
                if (n % 3 == 0):
                    fw("{0}".format(indent))
                fw("{:11d},".format(i))
                if (n % 3 == 2):
                    fw("\n")
            fw("};\n")

            bpy.data.meshes.remove(mesh)

        f.close()
        return {'FINISHED'}

    def parse_args(self):
        self.outfile = ""

        if ("--" in sys.argv) == False:
            return

        pos = sys.argv.index("--")
        pos += 1
        args = sys.argv[pos:]

        try:
            opts, args = getopt.getopt(args, 'o:', ["outfile="])
        except getopt.GetoptError as err:
            print(err)
            return

        for opt, arg in opts:
            if (opt in ("-o", "--outfile")):
                self.outfile = arg

def create_menu(self, context):
    self.layout.operator(Export_c.bl_idname, text="C header for OpenGL ES (.h)")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(create_menu)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(create_menu)

if __name__ == "__main__":
    register()
    bpy.ops.export_scene.c()
