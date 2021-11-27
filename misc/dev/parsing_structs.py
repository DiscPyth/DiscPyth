# flake8: noqa

from gsparse import make

Input = """type MessageEmbedVideo struct {
	URL    string `json:"url,omitempty"`
	Width  int    `json:"width,omitempty"`
	Height int    `json:"height,omitempty"`
}
"""

for s in make(Input):
    print(s)
