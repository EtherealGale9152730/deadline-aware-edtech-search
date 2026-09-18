from datetime import date

from edtech_search import Course, EdtechSearch, educator_report


def main() -> None:
    search = EdtechSearch("edtech-courses", 1536)
    search.create_collection()
    courses = [Course("python-basics", "Python basics", "Variables, loops, and functions", date(2026, 9, 15), "Ava")]
    search.add_courses(courses)
    matches = search.search("How do I write a loop?", date(2026, 9, 1))
    print(educator_report(matches, date(2026, 9, 1)))


if __name__ == "__main__":
    main()
