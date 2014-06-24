from PIL import Image
import subprocess
import math
import sys
import os

# Script Arguments

Institution = sys.argv[1]
Location    = sys.argv[2]

# Classes

# Local

class Local:
  base = os.path.dirname(os.path.realpath(__file__)) + os.sep + "components" + os.sep
  pathMap = {
    "static": "static" + os.sep,
    "screenshot": "screenshot" + os.sep,
    "phantomjs": "phantomjs" + os.sep + "rasterize.js",
  }

  @classmethod
  def path(cls, name):
    return cls.base + cls.pathMap[name]

# Source

class Source:
  base = "https://www.youvisit.com/"

  def __init__(self, options):
    self.url  = self.__class__.buildUrl(options["path"])
    self.name = options["name"]

  @classmethod
  def buildUrl(cls, path):
    return cls.base + path + Institution + "/" + Location + "/"

# DeviceProfile

class DeviceProfile:
  def __init__(self, options):
    res = options["resolution"]

    self.name             = options["name"]
    self.devicePixelRatio = options["device pixel ratio"]
    self.bar              = Image.open(Local.path("static") + self.name + ".png")
    self.resolution       = {
      "full":     res,
      "partial":  (res[0], res[1] - self.bar.size[1]),
      "real":     (self.downscale(res[0]), self.downscale(res[1] - self.bar.size[1]))
    }

  def downscale(self, res):
    return int(math.ceil(res / self.devicePixelRatio))

# Screenshot

class Screenshot:
  def __init__(self, options):
    self.src        = options["src"]
    self.profile    = options["profile"]
    self.filename   = Local.path("screenshot") + Institution + "." + Location + "." + options["src"].name + "." + options["profile"].name + ".png"
    self.resolution = `options["profile"].resolution["real"][0]` + "px" + "*" + `options["profile"].resolution["real"][1]` + "px"

    self.download()
    self.build()

  def download(self):
    subprocess.call(["phantomjs", Local.path("phantomjs"), self.src.url, self.filename, self.resolution])

  def build(self):
    image = Image.open(self.filename)
    image = image.resize(self.profile.resolution["partial"], Image.ANTIALIAS)
    
    composite = Image.new("RGB", self.profile.resolution["full"])
    composite.paste(image, (0, self.profile.bar.size[1]))
    composite.paste(self.profile.bar, (0, 0))
    composite.save(self.filename, "PNG")

# Local Variables

sources = [
  Source({ "name": "home", "path": "" }),
  Source({ "name": "tour", "path": "tour/" }),
  Source({ "name": "panoramas", "path": "tour/panoramas/" }),
  Source({ "name": "photos", "path": "tour/photos/" }),
  Source({ "name": "videos", "path": "tour/videos/" }),
]

profiles = [
  DeviceProfile({
    "name":                 "iphone35",
    "device pixel ratio":   2,
    "resolution":           (640, 960),
  }),
  DeviceProfile({
    "name":                 "iphone4",
    "device pixel ratio":   2,
    "resolution":           (640, 1136),
  }),
  DeviceProfile({
    "name":                 "android",
    "device pixel ratio":   1.5,
    "resolution":           (506, 900),
  })
]

for source in sources:
  for profile in profiles:
    Screenshot({
      "src": source,
      "profile": profile,
    })
