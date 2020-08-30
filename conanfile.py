from conans import ConanFile
from conans.tools import Git, cpu_count

import os

OS_MAP = {
    "Windows": "windows",
    "Linux": "linux",
    "Macos": "osx",
}

BIT_MAP = {
    "x86_64": 64,
    "armv8": 64,
}

LLVM_MAP = {
    "clang": True,
    "apple-clang": True,
}

BUILD_TYPE_MAP = {
    None: "debug",
    "Debug": "debug",
    "Release": "release",
    "MinSizeRel": "release",
    "RelWithDebInfo": "release",
}


class GodotCppConan(ConanFile):
    name = "godot-cpp"
    description = "C++ bindings for the Godot script API"
    license = "MIT"
    url = "https://github.com/fmorgner/conan-godot-cpp.git"
    author = "Felix Morgner"
    topics = ("game-engine", "game-development", "c++")
    settings = {
        "arch": None,
        "os": ["Windows", "Linux", "Macos"],
        "compiler": None,
        "build_type": None,
    }
    build_requires = ["scons/[~=3]"]

    @property
    def _platform(self):
        return OS_MAP[self.settings.get_safe("os")]

    @property
    def _bits(self):
        return BIT_MAP.get(self.settings.get_safe("arch"), 32)

    @property
    def _use_llvm(self):
        return LLVM_MAP.get(self.settings.get_safe("compiler"), False)

    @property
    def _target(self):
        return BUILD_TYPE_MAP[self.settings.get_safe("build_type")]

    def source(self):
        git = Git(folder="godot-cpp")
        git.clone(
            "https://github.com/godotengine/godot-cpp",
            branch=self.version,
            args="--recursive",
        )

    def build(self):
        self.run(
            " ".join([
                "scons",
                "-C",
                "\"{}\"".format(os.path.join(self.source_folder, "godot-cpp")),
                "platform={}".format(self._platform),
                "bits={}".format(self._bits),
                "use_llvm={}".format(self._use_llvm),
                "target={}".format(self._target),
                "generate_bindings=yes",
                "-j{}".format(cpu_count()),
            ])
        )

    def package(self):
        self.copy("*.hpp", dst="include/godot-cpp", src="godot-cpp/include")
        self.copy("*.h", dst="include/godot-native", src="godot-cpp/godot_headers")
        self.copy("*.a", dst="lib", src="godot-cpp/bin")
        self.copy("*.lib", dst="lib", src="godot-cpp/bin")

    def package_info(self):
        self.cpp_info.includedirs = [
            os.path.join("include", "godot-native"),
            os.path.join("include", "godot-cpp"),
            os.path.join("include", "godot-cpp", "core"),
            os.path.join("include", "godot-cpp", "gen"),
        ]
        library_base_name = "godot-cpp.{}.{}.{}".format(self._platform, self._target, self._bits)
        if self.settings.os == "Windows":
            self.cpp_info.libs = ["lib{}".format(library_base_name)]
        else:
            self.cpp_info.libs = [library_base_name]
