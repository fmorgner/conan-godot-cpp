from conans import ConanFile
from conans.tools import Git, cpu_count


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
    settings = {
        "arch": None,
        "os": ["Windows", "Linux", "Macos"],
        "compiler": None,
        "build_type": None,
    }

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
            [
                "scons",
                "-C",
                "{}/godot-cpp".format(self.source_folder),
                "platform={}".format(self._platform),
                "bits={}".format(self._bits),
                "use_llvm={}".format(self._use_llvm),
                "target={}".format(self._target),
                "-j{}".format(cpu_count()),
                "generate_bindings=yes",
            ]
        )

    def package(self):
        self.copy("*.hpp", dst="include/godot-cpp", src="godot-cpp/include")
        self.copy("*.h", dst="include/godot-native", src="godot-cpp/godot_headers")
        self.copy("*.a", dst="lib", src="godot-cpp/bin")
        self.copy("*.lib", dst="lib", src="godot-cpp/bin")

    def package_info(self):
        self.cpp_info.includedirs = [
            "include/godot-native",
            "include/godot-cpp",
            "include/godot-cpp/core",
            "include/godot-cpp/gen",
        ]
        self.cpp_info.libs = [
            "godot-cpp.{}.{}.{}".format(self._platform, self._target, self._bits)
        ]